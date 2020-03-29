import json
import shapely.geometry
import pyproj
import numpy as np
from Aggregator import TimeSmoothAggregatorKernelDensity
import numpy as np
from query_gmaps_places import latlong2meters_zurich, meters2latlong_zurich
from tqdm import tqdm
import random
import os
import pickle as pkl
import pandas
import datetime

#HEATMAP_FILE = 'template_heatmap.json'
HEATMAP_FILE = 'simple_heatmap.json'
#HEATMAP_FILE = 'restaurant_heatmap.json'


def open_sample_heatmap():
    # this is just an example I would require a similar layout
    with open(HEATMAP_FILE, 'r') as f:
        heatmap = json.load(f)
    return heatmap


def open_sample_dataset():
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

def find_place_by_id(id, track):
    for traj_entery in tqdm(track["timelineObjects"]):
        if "placeVisit" in traj_entery and "location" in traj_entery["placeVisit"]:
            place = traj_entery["placeVisit"]["location"]
            if place["placeId"] == id:
                return place
    print("ERROR: Place not found")
    return None


class HeatmapModel():
    def __init__(self, database=None):
        super().__init__()
        self.database = database or []
        # dataset_file = "zurich_dataset.pkl"
        dataset_file = "zurich_dataset_all.pkl"
        if not os.path.isfile(dataset_file):
            raise FileNotFoundError("Database does not exist")
        with open(dataset_file, "rb") as f:
            x = pkl.load(f)
            y = pkl.load(f)
            time = pkl.load(f)
        self.X = np.array([x, y, time]).T
        self.aggregator = TimeSmoothAggregatorKernelDensity()
        self.X[:, 2] = 0  # discard time
        self.aggregator.update(self.X)
        self.heatmap_sample_cnt = 10

    def track2matrix(self, track):
        point_list = []
        place_location_list = []
        place_id_list = []
        # Set up projections
        print("Parsing files into matrix")
        for traj_entery in tqdm(track["timelineObjects"]):
            # only use lines so far
            if "activitySegment" in traj_entery and "simplifiedRawPath" in traj_entery["activitySegment"]:
                for point in traj_entery["activitySegment"]["simplifiedRawPath"]["points"]:
                    x, y = latlong2meters_zurich(
                        np.array([point["latE7"] / 10000000]),
                        np.array([point["lngE7"] / 10000000])
                    )
                    point_list.append([
                        float(x[0]),
                        float(y[0]),
                        float(point["timestampMs"])
                    ])
            if "placeVisit" in traj_entery and "location" in traj_entery["placeVisit"]:
                point = traj_entery["placeVisit"]["location"]
                x, y = latlong2meters_zurich(
                    np.array([point["latitudeE7"] / 10000000]),
                    np.array([point["longitudeE7"] / 10000000])
                )
                place_location_list.append([
                    np.array(float(x[0])),
                    np.array(float(y[0])),
                    0.0
                ])
                place_id_list.append(point["placeId"])

        self.heat_matrix = np.array(point_list)
        print(f"self.heat_matrix.shape = {self.heat_matrix.shape}")
        return np.array(point_list, dtype=np.float64), np.array(place_location_list, dtype=np.float64), place_id_list


    def update_database(self, trajectory):
        self.database.append(trajectory)
        if len(self.database) > 0:
            self.X = np.concatenate((self.X, self.track2matrix(trajectory)[0]),axis=0)
            self.X[:, 2] = 0 # discard time
            self.aggregator.update(self.X)

    def get_heatmap(self):
        print("Retrieving heatmap samples")
        samples_locations, sample_scores = self.aggregator.sample_heatmap(self.heatmap_sample_cnt)
        feature_list = []
        lat, long = meters2latlong_zurich(samples_locations[:, 0], samples_locations[:, 1])
        time =  samples_locations[:, 2]

        for i in range(sample_scores.shape[0]):
            feature_list += [{
                    "type": "Feature",
                    "properties": {"mag": float("%.6f" % (sample_scores[i]*1000000)), "time": time[i]},
                    "geometry": {
                        "type": "Point",
                        "coordinates": [float("%.6f" % long[i]), float("%.6f" % lat[i]), 0]
                    }
            }]

        heatmap = {
            "type": "FeatureCollection",
            "features": feature_list
        }
        print("Heatmap samples returned")
        return heatmap


    # trajectory: of the sick person google location file
    # database: [traj0, traj1, ..., trajn]

    def get_risk_info(self, trajectory):
        X_track, X_Places, place_id = self.track2matrix(trajectory)
        # disregard time for now
        X_track[:,2] = 0
        X_Places[:,2] = 0
        print(X_track.shape)
        total_score, _, _ = self.aggregator.get_infection_likelihood(X_track)
        _, likelihoods, sorted_indices = self.aggregator.get_infection_likelihood(X_Places)

        total_score *= 1000000
        likelihoods *= 1000000

        most_risky_places = []

        i = 0
        for index in sorted_indices:
            place = find_place_by_id(place_id[index], trajectory)
            most_risky_places.append({
                **place,
                "risk_value": likelihoods[index]
            })
            i += 1
            if i == 3:
                break
        # risk value come from the tracks the person took
        # most_risky_places is just the places with the highest risk values
        # maybe just the places in the trajectory and in the sick db
        response = {
            'risk_value': total_score,
            'most_risky_places': most_risky_places
        }
        # self.update_database(trajectory)
        print(response)
        return response
