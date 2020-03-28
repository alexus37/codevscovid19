from heatmap import open_sample_dataset
from query_gmaps_places import meters2latlong_zurich, latlong2meters_zurich

lat, long, time = open_sample_dataset()
lat = lat
long = long
time = time

import os
import pickle as pkl

dataset_file = "zurich_dataset_all.pkl"
if not os.path.isfile(dataset_file):
    x, y = latlong2meters_zurich(lat, long)
    with open(dataset_file, "wb") as f:
        pkl.dump(x, f)
        pkl.dump(y, f)
        pkl.dump(time, f)
else:
    print("File already there. Won't overwrite.")