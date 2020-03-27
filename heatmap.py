import json

#HEATMAP_FILE = 'template_heatmap.json'
HEATMAP_FILE = 'simple_heatmap.json'

class HeatmapModel():
    def __init__(self, database):
        super().__init__()
        self.database = database

    def update_database(self, trajectory):
        self.database.append(trajectory)

    def get_heatmap(self):
        # this is just an example I would require a similar layout

        with open(HEATMAP_FILE, 'r') as f:
            heatmap = json.load(f)
        return heatmap


    # trajectory: of the sick person google location file
    # database: [traj0, traj1, ..., trajn]

    def get_risk_info(self, trajectory):
        # this we dont know in detail yet
        response = {'risk_value': 0.75}

        self.update_database(trajectory)
        return response
