import json

def get_heatmap():
    # this is just an example I would require a similar layout

    with open('template_heatmap.json', 'r') as f:
        heatmap = json.load(f)
    return heatmap