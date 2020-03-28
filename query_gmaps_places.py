import shapely.geometry
import pyproj
import random
import json
import sys
import requests
from tqdm import tqdm

ZURICH_LEFT = 8.5099
ZURICH_RIGHT = 8.5683
ZURICH_TOP = 47.3887
ZURICH_BOTTOM = 47.3564
def get_url(lat, long, key):
    BASE_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    final_url = f"{BASE_URL}?key={key}&location={lat},{long}&rankby=distance&type=restaurant"
    return final_url

def main(key):
    # Set up projections
    p_ll = pyproj.Proj(init='epsg:4326')
    p_mt = pyproj.Proj(init='epsg:3857') # metric; same as EPSG:900913

    # Create corners of rectangle to be transformed to a grid

    se = shapely.geometry.Point((ZURICH_TOP, ZURICH_RIGHT))
    nw = shapely.geometry.Point((ZURICH_BOTTOM, ZURICH_LEFT))

    stepsize = 750 # grid step size in meter

    # Project corners to target projection
    s = pyproj.transform(p_ll, p_mt, nw.x, nw.y) # Transform NW point to 3857
    e = pyproj.transform(p_ll, p_mt, se.x, se.y) # .. same for SE

    # Iterate over 2D area
    grid_points = []
    x = s[0]
    while x < e[0]:
        y = s[1]
        while y < e[1]:
            p = shapely.geometry.Point(pyproj.transform(p_mt, p_ll, x, y))
            grid_points.append(p)
            y += stepsize
        x += stepsize

    print(len(grid_points))
    i = 0
    for grid_point in tqdm(grid_points):
        gmaps_url = get_url(grid_point.x, grid_point.y, key)

        restaurants = requests.get(gmaps_url)
        data = restaurants.json()
        with open(f"google_places_restaurantes/restaurants_{i}.json", 'w') as f:
            json.dump(data, f)
        i += 1
    # simple_feature_map = {
    #     "type": "FeatureCollection",
    #     "features": [
    #         {
    #             "type": "Feature",
    #             "properties": {
    #                 "mag": random.random(),
    #                 "time": random.randint(1585339300000, 1585339324410)
    #             },
    #             "geometry": {
    #                 "type": "Point",
    #                 "coordinates": [
    #                     grid_point.y, # lon
    #                     grid_point.x, # lat
    #                     0
    #                 ]
    #             },
    #         } for grid_point in grid_points
    #     ]
    # }


    # with open('simple_heatmap.json', 'w') as f:
    #     json.dump(simple_feature_map, f)


if __name__ == '__main__':
    main(sys.argv[1])