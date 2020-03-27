require([
  "esri/Map",
  "esri/layers/GeoJSONLayer",
  "esri/views/MapView"
], function(Map, GeoJSONLayer, MapView) {
  // If GeoJSON files are not on the same domain as your website, a CORS enabled server
  // or a proxy is required.
  const url = `${location.href}/heatmap`;

  // Paste the url into a browser's address bar to download and view the attributes
  // in the GeoJSON file. These attributes include:
  // * mag - magnitude
  // * type - earthquake or other event such as nuclear test
  // * place - location of the event
  // * time - the time of the event
  // Use the Arcade Date() function to format time field into a human-readable format

  //   const template = {
  //     title: "Earthquake Info",
  //     content: "Magnitude {mag} {type} hit {place} on {time}",
  //     fieldInfos: [
  //       {
  //         fieldName: "time",
  //         format: {
  //           dateFormat: "short-date-short-time"
  //         }
  //       }
  //     ]
  //   };

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
    maxPixelIntensity: 5000
  };

  const geojsonLayer = new GeoJSONLayer({
    url: url,
    renderer: renderer //optional
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
