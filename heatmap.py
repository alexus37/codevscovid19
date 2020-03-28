import json
import shapely.geometry
import pyproj
import numpy as np
from Aggregator import TimeSmoothAggregatorKernelDensity
import numpy as np
from query_gmaps_places import latlong2meters_zurich, meters2latlong_zurich
from tqdm import tqdm
import random

#HEATMAP_FILE = 'template_heatmap.json'
HEATMAP_FILE = 'simple_heatmap.json'
#HEATMAP_FILE = 'restaurant_heatmap.json'


def open_sample_heatmap():
    # this is just an example I would require a similar layout
    with open(HEATMAP_FILE, 'r') as f:
        heatmap = json.load(f)
    return heatmap

def open_sample_dataset():
    import pandas
    import datetime

    dataframe = pandas.read_csv('zurich_dataset.csv')
    array = dataframe.to_numpy()
    lat = array[:, 1]
    long = array[:, 2]
    dataframe['time'] = dataframe['time'].str.replace("-", "")
    dataframe['time'] = dataframe['time'].str.replace(" ", "")
    dataframe['time'] = dataframe['time'].str.replace(":", "")
    dataframe['time'] = dataframe['time'].str.replace("\+0000", "")
    # dataframe['time'] = dataframe.dt.strftime("%Y%m%D%H%M%S")
    dataframe['time'] = pandas.to_datetime(dataframe['time'], format="%Y%m%d%H%M%S")
    time = dataframe['time'].values.astype(float)
    return [lat, long, time]
    # with open('zurich_dataset.csv' ,'r') as f:
    #     csv_reader = csv.reader(f, delimiter=',')

class HeatmapModel():
    def __init__(self, database):
        super().__init__()
        if len(database) == 0:
            lat, long, time = open_sample_dataset()
            lat = lat[:10000]
            long = long[:10000]
            time = time[:10000]
            self.database = [[lat, long, time], ]
            import os
            import pickle as pkl
            dataset_file = "zurich_dataset.pkl"
            if not os.path.isfile(dataset_file):
                x, y = latlong2meters_zurich(lat, long)
                with open(dataset_file, "wb") as f:
                    pkl.dump(x, f)
                    pkl.dump(y, f)
                    pkl.dump(time, f)
                return
            else:
                with open(dataset_file, "rb") as f:
                    x = pkl.load(f)
                    y = pkl.load(f)
                    time = pkl.load(f)
            self.X = np.array([x, y, time]).T
        else:
            self.database = database
            self.X = self.database2matrix(self.database)
        self.aggregator = TimeSmoothAggregatorKernelDensity()

        if len(self.database) > 0:
            self.X[:, 2] = 0 # discard time
            self.aggregator.update(self.X)

    def database2matrix(self, database):
        x, y = latlong2meters_zurich(database[0][0][:2000], database[0][1][:2000])
        return np.array([x, y, database[0][2][:2000]]).T

        point_list = []
        # Set up projections
        p_ll = pyproj.Proj(init='epsg:4326')
        p_mt = pyproj.Proj(init='epsg:3857') # metric; same as EPSG:900913
        print("Parsing files into matrix")
        for trajectory in tqdm(database):
            for traj_entery in trajectory["timelineObjects"]:
                # only use lines so far
                if "activitySegment" in traj_entery and "simplifiedRawPath" in traj_entery["activitySegment"]:
                    for point in traj_entery["activitySegment"]["simplifiedRawPath"]["points"]:
                        s_point = shapely.geometry.Point((
                            point["latE7"] / 10000000,
                            point["lngE7"] / 10000000
                        ))

                        # Project corners to target projection
                        s_point = pyproj.transform(p_ll, p_mt, s_point.x, s_point.y) # Transform NW point to 3857
                        point_list.append([
                            s_point[0],
                            s_point[1],
                            point["timestampMs"]
                        ])
        self.heat_matrix = np.array(point_list)
        print(f"self.heat_matrix.shape = {self.heat_matrix.shape}")


    def update_database(self, trajectory):
        self.database.append(trajectory)
        if len(self.database) > 0:
            X = self.database2matrix(self.database)
            X[:, 2] = 0 # discard time
            self.aggregator.update(X)

    def get_heatmap(self):
        print("Retrieving heatmap samples")
        sample_heatmap = open_sample_heatmap()
        samples_locations, sample_scores = self.aggregator.sample_heatmap(100)
        feature_list = []
        lat, long = meters2latlong_zurich(samples_locations[:, 0], samples_locations[:, 1])
        time =  samples_locations[:, 2]

        for i in range(sample_scores.shape[0]):
            feature_list += [{
                    "type": "Feature",
                    "properties": {"mag": random.randint(0, 100), "time": time[i]},
                    "geometry": {
                        "type": "Point",
                        "coordinates": [long[i], lat[i], 0]
                    }
            }]

        heatmap = {
            "type": "FeatureCollection",
            "features": feature_list
        }
        with open(HEATMAP_FILE, 'r') as f:
            heatmap = json.load(f)
        print("Heatmap samples returned")
        return heatmap


    # trajectory: of the sick person google location file
    # database: [traj0, traj1, ..., trajn]

    def get_risk_info(self, trajectory):
        # risk value come from the tracks the person took
        # most_risky_places is just the places with the highest risk values
        # maybe just the places in the trajectory and in the sick db
        response = {
            'risk_value': 0.75,
            'most_risky_places': [
                {
                    "latitudeE7": 473743221,
                    "longitudeE7": 85509812,
                    "placeId": "ChIJi4WVWJ-gmkcRz9p-0FL6ULo",
                    "address": "Rämistrasse 71\n8006 Zürich\nSchweiz",
                    "name": "University of Zurich",
                    "risk_value": 0.98
                },
                {
                    "latitudeE7": 473657945,
                    "longitudeE7": 85477139,
                    "placeId": "ChIJ0awoNlOnmkcRcPkN_XiQfz0",
                    "address": "Goethestrasse 14\n8001 Zürich\nSchweiz",
                    "name": "Arzthaus Zürich Stadelhofen",
                    "risk_value": 0.86
                },
                {
                    "latitudeE7": 473882334,
                    "longitudeE7": 85180000,
                    "placeId": "ChIJVVWVpkAKkEcRYMSNQ2QmY-Y",
                    "address": "Pfingstweidstrasse 16\n8005 Zürich\nSchweiz",
                    "name": "Kulturpark",
                    "risk_value": 0.67
                }
            ]
        }
        self.update_database(trajectory)
        return response
