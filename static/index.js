require([
  "esri/Map",
  "esri/layers/GeoJSONLayer",
  "esri/views/MapView",
], function(Map, GeoJSONLayer, MapView) {
  // If GeoJSON files are not on the same domain as your website, a CORS enabled server
  // or a proxy is required.
  const url = `${location.href}/heatmap`;

  const renderer = {
    type: "heatmap",
    field: "mag",
    colorStops: [
      { ratio: 0, color: "rgba(255, 255, 255, 0)" },
      { ratio: 0.2, color: "rgba(255, 255, 255, 1)" },
      { ratio: 0.5, color: "rgba(255, 140, 0, 1)" },
      { ratio: 0.8, color: "rgba(255, 140, 0, 1)" },
      { ratio: 1, color: "rgba(255, 0, 0, 1)" }
    ],
    minPixelIntensity: 0,
    maxPixelIntensity: 10
  };

  const geojsonLayer = new GeoJSONLayer({
    url: url,
    renderer: renderer,
    labelsVisible: false,
    labelingInfo: []
  });

  const map = new Map({
    basemap: "dark-gray",
    layers: [geojsonLayer]
  });

  const view = new MapView({
    container: "map",
    center: [8.538658, 47.377782],
    zoom: 14,
    map: map
  });
});

Dropzone.options.healthyDropzone = {
  init: function() {
    this.on("addedfile", function(file) { 
      console.log("added file");
    });
    this.on("success", function(file) { console.log("success") });
  }
}

Dropzone.options.infectedDropzone = {
  init: function() {
    this.on("success", function(file) { 
      console.log("Great success.")
     });
  }
}
