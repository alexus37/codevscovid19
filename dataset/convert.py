import pandas as pd
import random
import numpy as np
import json
import os
import glob
from tqdm import tqdm
import multiprocessing
from geopy.distance import great_circle
from math import radians, cos, sin, asin, sqrt

PROXIMITY_THRESHOLD = 750  # TODO tweak to get the right amounts of visits
RESTAURANTS_FOLDER = 'google_places_restaurants/'


def haversine(point1, point2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lat1, lon1, lat2, lon2 = map(radians, [*point1, *point2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    # Radius of earth in kilometers is 6371
    m = 6371* c * 1000
    return m


def distance(point1, point2):
    return haversine(point1, point2)
    return great_circle(point1, point2).km *1000


def _parse_restaurant(data):
    return {
        'latitude': data['geometry']['location']['lat'],
        'longitude': data['geometry']['location']['lng'],
        'address': data['vicinity'],
        'name': data['name'],
        'id': data['place_id']
    }


def parse_restaurants(folder):
    restaurants = []
    for fn in glob.glob(folder + '/*.json'):
        with open(fn, 'r') as f:
            data = json.load(f)
        restaurants.extend([_parse_restaurant(rdata) for rdata in data['results']])

    return pd.DataFrame(restaurants)

restaurants = parse_restaurants(RESTAURANTS_FOLDER)

def visit_duration():
    '''
    random function to determine the visit time (in ms)
    '''
    return random.randint(900000, 5400000)  # 15 minutes to 1.5 hours


def determine_visits(points, restaurants):
    visits = {}  # map points to restaurants
    for rindex, restaurant in restaurants.iterrows():
        distances = points.apply(lambda point: distance((restaurant['latitude'], restaurant['longitude']), (point['latitude'], point['longitude'])), axis=1)
        if distances.min() < PROXIMITY_THRESHOLD:
            visits[distances.argmin()] = {'restaurant_index': rindex, 'duration': visit_duration()}

    return visits

def activitySegment(points):
    return {
        'activitySegment': {
            'startLocation': {
                'latitudeE7': points.iloc[0]['latitude'] * 1E7,
                'longitudeE7': points.iloc[0]['longitude'] * 1E7,
            },
            'endLocation': {
                'latitudeE7': points.iloc[-1]['latitude'] * 1E7,
                'longitudeE7': points.iloc[-1]['longitude'] * 1E7,
            },
            'duration': {
                'startTimestampMs': points['time'].min(),
                'endTimestampMs': points['time'].max()
            },
            'distance': 9999,  # no need to compute this.
            'activityType': 'none',  # no need
            'confidence': 'none',  # no need
            'activities': [],  # no need
            'simplifiedRawPath': {
                'points': [{
                    'latE7': p['latitude'] * 1E7,
                    'lngE7': p['longitude'] * 1E7,
                    'timestampMs': p['time'],
                    'accuracyMeters': random.randint(5, 250)}
                        for _, p in points.iterrows()
                ]
            }
        }
    }


def placeVisit(point, restaurant, duration):
    return {
        "placeVisit" : {
            "location" : {
                "latitudeE7" : restaurant['latitude'] * 1E7,  # restaurant location
                "longitudeE7" : restaurant['longitude'] * 1E7,
                "placeId" : restaurant['id'],
                "address" : restaurant['address'],
                "name": restaurant['name'],
                "semanticType" : "none", # unused
                "sourceInfo" : {
                    "deviceTag": -1
                },
                "locationConfidence" : 100  # unused
            },
            "duration" : {
                "startTimestampMs" : point.time,
                "endTimestampMs" : point.time + duration
            },
            "placeConfidence" : "HIGH_CONFIDENCE",  # unused
            "centerLatE7" : point['latitude'] * 1E7,  # GPS location
            "centerLngE7" : point['longitude'] * 1E7,
            "visitConfidence" : 100,  # unused
            "otherCandidateLocations" : [],  #unused
            "editConfirmationStatus" : "none"  # unused
        }
  }


def compute_track(v):
    trackname, points = v
    # print(trackname, len(points))
    points.reset_index(inplace=True)
    visits = determine_visits(points, restaurants)
    print(trackname, len(visits))

    last_point = 0
    timelineObjects = []
    for point_index in sorted(visits.keys()):
        if point_index > 0:
            timelineObjects.append(activitySegment(points.iloc[last_point:point_index]))
        place = restaurants.loc[visits[point_index]['restaurant_index']]
        duration = visits[point_index]['duration']
        timelineObjects.append(placeVisit(points.iloc[point_index], place, duration))

        # generate offset for subsequent points because of visit..
        points.iloc[point_index+1:]['time'] += duration

        last_point = point_index

    # add last segment
    if last_point - 1 < len(points):
        timelineObjects.append(activitySegment(points.iloc[last_point:]))

    if trackname:
        with open(f'tracks/{trackname}.json', 'w') as f:
            json.dump(timelineObjects, f)

DEBUG = False

def main():
    df = pd.read_csv('./zurich_dataset.csv', parse_dates=['time'], infer_datetime_format=True)
    df['time'] = df['time'].apply(lambda v: (v.to_datetime64() - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's'))

    try:
        os.mkdir('tracks')
    except FileExistsError:
        pass

    grouped = df.groupby('track_name')
    if not DEBUG:
        pool = multiprocessing.Pool(6)
        out = pool.map(compute_track, grouped)
    else:
        for track_name, points in tqdm(grouped):
            compute_track((track_name, points))


if __name__ == '__main__':
    main()
