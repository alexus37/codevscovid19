top_left = (47.398408, 8.488119)
bottom_left = (47.353059, 8.488119)
top_right = (47.398408, 8.554656)

import shapely.geometry
import pyproj
import random
import json
import sys
import requests
from tqdm import tqdm

p_ll = pyproj.Proj(init='epsg:4326')
p_mt = pyproj.Proj(init='epsg:3857') # metric; same as EPSG:900913# Create corners of rectangle to be transformed to a gridse = shapely.geometry.Point((ZURICH_TOP, ZURICH_RIGHT))# Project corners to target projection
top_left_m = pyproj.transform(p_ll, p_mt, top_left[1], top_left[0])
top_right_m = pyproj.transform(p_ll, p_mt, top_right[1], top_right[0])
bottom_left_m = pyproj.transform(p_ll, p_mt, bottom_left[1], bottom_left[0])


def translate(latitude, longitude):
    x = top_left_m[0] + ((longitude - top_left[1]) * 7406.86 / (top_right[1] - top_left[1]))
    y = top_left_m[1] + ((latitude - top_left[0]) * -7454.7 / (bottom_left[0] - top_left[0]))

    return (x, y)


def translate_reverse(x, y):
    longitude = top_left[1] + ((x - top_left_m[0]) * (top_right[1] - top_left[1]) / (top_right_m[0] - top_left_m[0]))
    latitude =  top_left[0] +  ((-y + top_left_m[1]) * (top_left[0] - bottom_left[0]) / (bottom_left_m[1] - top_left_m[1]))

    return (longitude, latitude)
