import tornado.ioloop
import tornado.web
from tornado.escape import json_decode, json_encode
import os
import glob
import json
import uuid
from heatmap import HeatmapModel

ROOT = os.path.join(os.path.dirname(__file__), "static")
PORT = 8000
DATA_DIR = f"./data"

class UploadHandler(tornado.web.RequestHandler):
    def initialize(self, heatmapModel):
        self.heatmapModel = heatmapModel
    def post(self):
        trajectory = self.request.files['file'][0]['body']
        trajectory_json = trajectory.decode('utf8').replace("'", '"')
        trajectory_json = json.loads(trajectory_json)
        infected = self.get_body_argument("infected", default=False)
        print(f"Is infected: {infected}")
        if not infected:
            response = self.heatmapModel.get_risk_info(trajectory_json)
        else:
            #  save to file
            self.heatmapModel.update_database(trajectory_json)
            response = {
                'message' : 'Thanks for helping out!!'
            }
        with open(f'{DATA_DIR}/{uuid.uuid4()}.json', 'w') as fp:
                json.dump(trajectory_json, fp)

        self.write(json.dumps(response))
        self.finish()  # Without this the client's request will hang

class HeatmapHandler(tornado.web.RequestHandler):
    def initialize(self, heatmapModel):
        self.heatmapModel = heatmapModel
    # returns the heatmap
    def get(self):
        response = self.heatmapModel.get_heatmap()
        self.write(json.dumps(response))
        self.finish()  # Without this the client's request will hang

def make_app():
    database = []
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    for file in glob.glob(f"{DATA_DIR}/*.json"):
        with open(file) as json_file:
            database.append(json.load(json_file))

    heatmapModel = HeatmapModel(database)

    return tornado.web.Application([
        (r"/heatmap", HeatmapHandler, {'heatmapModel': heatmapModel}),
        (r"/upload", UploadHandler, {'heatmapModel': heatmapModel}),
        (r"/(.*)", tornado.web.StaticFileHandler, {"path": ROOT, "default_filename": "index.html"})
    ])  # URL Mapping

if __name__ == "__main__":
    app = make_app()
    print(f"Starting  server on port = {PORT}")
    app.listen(PORT)    # Port Number
    tornado.ioloop.IOLoop.current().start()
