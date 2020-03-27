import json

def get_heatmap(database):
    # this is just an example I would require a similar layout

    with open('template_heatmap.json', 'r') as f:
        heatmap = json.load(f)
    return heatmap


# trajectory: of the sick person google location file
# database: [traj0, traj1, ..., trajn]

def get_risk_info(trajectory, database):
    # this we dont know in detail yet
    response = {'risk_value': 0.75}
    return response
