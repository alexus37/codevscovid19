import shapely.geometry
import pyproj
import random
import json

ZURICH_LEFT = 8.4588
ZURICH_RIGHT = 8.5755
ZURICH_TOP = 47.4133
ZURICH_BOTTOM = 47.3488
# Set up projections
p_ll = pyproj.Proj(init='epsg:4326')
p_mt = pyproj.Proj(init='epsg:3857') # metric; same as EPSG:900913

# Create corners of rectangle to be transformed to a grid

se = shapely.geometry.Point((ZURICH_TOP, ZURICH_RIGHT))
nw = shapely.geometry.Point((ZURICH_BOTTOM, ZURICH_LEFT))

stepsize = 500 # grid step size in meter

# Project corners to target projection
s = pyproj.transform(p_ll, p_mt, nw.x, nw.y) # Transform NW point to 3857
e = pyproj.transform(p_ll, p_mt, se.x, se.y) # .. same for SE

# Iterate over 2D area
gridpoints = []
x = s[0]
while x < e[0]:
    y = s[1]
    while y < e[1]:
        p = shapely.geometry.Point(pyproj.transform(p_mt, p_ll, x, y))
        gridpoints.append(p)
        y += stepsize
    x += stepsize

print(len(gridpoints))

simple_feature_map = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "mag": random.random(),
                "time": random.randint(1585339300000, 1585339324410)
            },
            "geometry": {
                "type": "Point",
                "coordinates": [
                    grid_point.y,
                    grid_point.x,
                    0
                ]
            },
        } for grid_point in gridpoints
    ]
}


with open('simple_heatmap.json', 'w') as f:
    json.dump(simple_feature_map, f)