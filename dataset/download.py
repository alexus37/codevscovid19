'''
Generation of test data set

We can get GPS locations as documented from here https://wiki.openstreetmap.org/wiki/API_v0.6#Retrieving_GPS_points

In violation of the GPX standard when downloading public GPX traces through the API, all waypoints of non-trackable traces are randomized (or rather sorted by lat/lon) and delivered as one trackSegment for privacy reasons.
Get GPS Points: Get /api/0.6/trackpoints?bbox=left,bottom,right,top&page=pageNumber
where:
    left is the longitude of the left (westernmost) side of the bounding box.
    bottom is the latitude of the bottom (southernmost) side of the bounding box.
    right is the longitude of the right (easternmost) side of the bounding box.
    top is the latitude of the top (northernmost) side of the bounding box.

https://api.openstreetmap.org/api/0.6/trackpoints?bbox=0,51.5,0.25,51.75&page=0  # each page has 5000 entries
'''

import requests
import itertools
import logging
import gpxpy
import pandas as pd
from tqdm import tqdm


API_URL = 'https://api.openstreetmap.org/api/0.6/trackpoints.json?bbox={left},{bottom},{right},{top}&page={page}'
ZURICH_LEFT = 8.4588
ZURICH_RIGHT = 8.5755
ZURICH_TOP = 47.4133
ZURICH_BOTTOM = 47.3488


def _query_api(page):
    logging.info(f'querying page {page}')
    response = requests.get(API_URL.format(left=ZURICH_LEFT, bottom=ZURICH_BOTTOM, right=ZURICH_RIGHT, top=ZURICH_TOP, page=page))
    gpx_data = gpxpy.parse(response.text)
    return gpx_data


if __name__ == '__main__':
    page = 0
    dfs = []
    for i in tqdm(itertools.count()):
        page_data =_query_api(i)
        if len(page_data.tracks) == 0:
            break
        for track in page_data.tracks:
            dfs.append(pd.DataFrame([
                {'latitude': point.latitude, 'longitude': point.longitude, 'time': point.time, 'track_name': track.name}
                for point in track.segments[0].points
            ]))
        if i % 10 == 0:
            pd.concat(dfs).to_csv('zurich_dataset.csv')
    df = pd.concat(dfs)
    df.to_csv('zurich_dataset.csv')
