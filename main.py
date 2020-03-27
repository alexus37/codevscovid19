import tornado.ioloop
import tornado.web
from tornado.escape import json_decode, json_encode
import os
import json
import uuid

ROOT = os.path.dirname(__file__)
PORT = 8888



class UploadHandler(tornado.web.RequestHandler):
    def post(self):
        fileinfo = self.request.files['filearg'][0]
        print (f"fileinfo is {fileinfo}")

        response = {'personalInfo': 'info'}

        self.write(json.dumps(response))
        self.finish()  # Without this the client's request will hang

class HeatmapHandler(tornado.web.RequestHandler):
    # returns the heatmap
    def post(self):
        response = {'heatmapdata': '12345'}
        self.write(json.dumps(response))
        self.finish()  # Without this the client's request will hang

def make_app():
    return tornado.web.Application([
        (r"/heatmap", HeatmapHandler),
        (r"/upload", UploadHandler),
        (r"/(.*)", tornado.web.StaticFileHandler, {"path": ROOT, "default_filename": "index.html"})
    ])  # URL Mapping

if __name__ == "__main__":
    app = make_app()
    print(f"Starting  server on port = {PORT}")
    app.listen(PORT)    # Port Number
    tornado.ioloop.IOLoop.current().start()
