from heatmap import open_sample_dataset
from latlng_to_meters import translate

lat, lng, time = open_sample_dataset()

import os
import pickle as pkl


dataset_file = "zurich_dataset_all2.pkl"
if not os.path.isfile(dataset_file):
    x, y = translate(lng, lat)
    with open(dataset_file, "wb") as f:
        pkl.dump(x, f)
        pkl.dump(y, f)
        pkl.dump(time, f)
else:
    print("File already there. Won't overwrite.")
