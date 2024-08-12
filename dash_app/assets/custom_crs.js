// custom_crs.js

// Define the EPSG:4269 CRS using Proj4Leaflet

// L.CRS.EPSG4269 = L.extend({}, L.CRS, {
//     code: 'EPSG:4269',
//     projection: L.Projection.LonLat, // Typically LonLat for geographic coordinate systems
//     transformation: new L.Transformation(1 / 360, 0.5, -1 / 360, 0.5),
//     scale: function (zoom) {
//         return 256 * Math.pow(2, zoom);
//     }
// });

// // Initialize the map with EPSG:4269 CRS
// L.Map.addInitHook(function () {
//     this.options.crs = L.CRS.EPSG4269;
// });


// L.CRS.EPSG102003 = L.extend({}, L.CRS, {
//     code: 'EPSG:102003',
//     projection: L.Projection.Laea,  // Using Albers Equal Area Conic projection
//     transformation: new L.Transformation(1 / 360, 0.5, -1 / 360, 0.5),
//     scale: function (zoom) {
//         return 256 * Math.pow(2, zoom);
//     },
//     infinite: true
// });

// // Apply the custom CRS to the map
// L.Map.addInitHook(function () {
//     this.options.crs = L.CRS.EPSG102003;
// });