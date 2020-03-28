import pandas as pd
import random
import numpy as np
import json
import os

df = pd.read_csv('./zurich_dataset.csv', parse_dates=['time'], infer_datetime_format=True)
df['time'] = df['time'].apply(lambda v: (v.to_datetime64() - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's'))

try:
    os.mkdir('tracks')
except FileExistsError:
    pass

for track_name, points in df.groupby('track_name'):
    data = {'timelineObjects': [
        {
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
                    'startTimestampMs': df['time'].min(),
                    'endTimestampMs': df['time'].max()
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
    ]}
    if track_name:
        with open(f'tracks/{track_name}.json', 'w') as f:
            json.dump(data, f)
