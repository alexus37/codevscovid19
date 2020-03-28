import json

#HEATMAP_FILE = 'template_heatmap.json'
#HEATMAP_FILE = 'simple_heatmap.json'
HEATMAP_FILE = 'restaurant_heatmap.json'

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
        # risk value come from the tracks the person took
        # most_risky_places is just the places with the highest risk values
        # maybe just the places in the trajectory and in the sick db
        response = {
            'risk_value': 0.75,
            'most_risky_places': [
                {
                    "latitudeE7": 473743221,
                    "longitudeE7": 85509812,
                    "placeId": "ChIJi4WVWJ-gmkcRz9p-0FL6ULo",
                    "address": "Rämistrasse 71\n8006 Zürich\nSchweiz",
                    "name": "University of Zurich",
                    "risk_value": 0.98
                },
                {
                    "latitudeE7": 473657945,
                    "longitudeE7": 85477139,
                    "placeId": "ChIJ0awoNlOnmkcRcPkN_XiQfz0",
                    "address": "Goethestrasse 14\n8001 Zürich\nSchweiz",
                    "name": "Arzthaus Zürich Stadelhofen",
                    "risk_value": 0.86
                },
                {
                    "latitudeE7": 473882334,
                    "longitudeE7": 85180000,
                    "placeId": "ChIJVVWVpkAKkEcRYMSNQ2QmY-Y",
                    "address": "Pfingstweidstrasse 16\n8005 Zürich\nSchweiz",
                    "name": "Kulturpark",
                    "risk_value": 0.67
                }
            ]
        }

        self.update_database(trajectory)
        return response
