import shapely.geometry
import pyproj
import random
import json
import sys
import requests
import glob
from tqdm import tqdm

DATA_DIR = "google_places_restaurantes/"

def main():
    restaurants_list = []
    for file in glob.glob(f"{DATA_DIR}/*.json"):
            with open(file) as json_file:
                restaurants_list.append(json.load(json_file))
    features = []
    for restaurants in tqdm(restaurants_list):
        for restaurant in restaurants["results"]:
            features.append({
                "type": "Feature",
                "properties": {
                    "mag": random.random(),
                    "time": random.randint(1585339300000, 1585339324410)
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        restaurant["geometry"]["location"]["lng"], # lon
                        restaurant["geometry"]["location"]["lat"], # lat
                        0
                    ]
                },
            })
    print(f'Create {len(features)} features')
    simple_feature_map = {
        "type": "FeatureCollection",
        "features": features
    }


    with open('restaurant_heatmap.json', 'w') as f:
        json.dump(simple_feature_map, f)


if __name__ == '__main__':
    main()