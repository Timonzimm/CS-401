var d3 = require('d3');
var $ = require('jquery');
var countries = require('./countries.geo.json');

// DEFINE VARIABLES
// Define size of map group
// Full world map is 2:1 ratio
// Using 12:5 because we will crop top and bottom of map
w = 3000;
h = 1250;
// variables for catching min and max zoom factors
var minZoom;
var maxZoom;
var active = d3.select(null);

// DEFINE FUNCTIONS/OBJECTS
// Define map projection
var projection = d3
    .geoNaturalEarth1()
    .scale([w / (2 * Math.PI)]) // scale to fit group width
    .translate([w / 2.1, h / 1.7]);

// Define map path
var path = d3
    .geoPath()
    .projection(projection);

// Create function to apply zoom to countriesGroup
function zoomed() {
    t = d3
        .event
        .transform;
    countriesGroup
        .attr("transform", "translate(" + [t.x, t.y] + ")scale(" + t.k + ")");
}

// Define map zoom behaviour
var zoom = d3
    .zoom()
    .on("zoom", zoomed);

// Function that calculates zoom/pan limits and sets zoom to default value 
function initiateZoom() {
    // Define a "minzoom" whereby the "Countries" is as small possible without leaving white space at top/bottom or sides
    minZoom = Math.max($("#map-holder").width() / w, $("#map-holder").height() / h);
    // set max zoom to a suitable factor of this value
    maxZoom = 20 * minZoom;
    // set extent of zoom to chosen values
    // set translate extent so that panning can't cause map to move out of viewport
    zoom
        .scaleExtent([minZoom, maxZoom])
        .translateExtent([
            [0, 0],
            [w, h]
        ]);
    // define X and Y offset for centre of map to be shown in centre of holder
    midX = ($("#map-holder").width() - minZoom * w) / 2;
    midY = ($("#map-holder").height() - minZoom * h) / 2;
    // change zoom transform to min zoom and centre offsets
    svg.transition().duration(500).call(zoom.transform, d3.zoomIdentity.translate(midX, midY).scale(minZoom));
}


// on window resize
$(window).resize(function () {
    // Resize SVG
    svg
        .attr("width", $("#map-holder").width())
        .attr("height", $("#map-holder").height());
    reset();
});

// create an SVG
var svg = d3
    .select("#map-holder")
    .append("svg")
    // set to the same size as the "map-holder" div
    .attr("width", $("#map-holder").width())
    .attr("height", $("#map-holder").height())

function boxZoom(box, centroid, paddingPerc) {
    minXY = box[0];
    maxXY = box[1];
    // find size of map area defined
    zoomWidth = Math.abs(minXY[0] - maxXY[0]);
    zoomHeight = Math.abs(minXY[1] - maxXY[1]);
    // find midpoint of map area defined
    zoomMidX = centroid[0];
    zoomMidY = centroid[1];
    // increase map area to include padding
    zoomWidth = zoomWidth * (1 + paddingPerc / 100);
    zoomHeight = zoomHeight * (1 + paddingPerc / 100);
    // find scale required for area to fill svg
    maxXscale = $("#map-holder").width() / zoomWidth;
    maxYscale = $("#map-holder").height() / zoomHeight;
    zoomScale = Math.min(maxXscale, maxYscale);
    // handle some edge cases
    // limit to max zoom (handles tiny countries)
    zoomScale = Math.min(zoomScale, maxZoom);
    // limit to min zoom (handles large countries and countries that span the date line)
    zoomScale = Math.max(zoomScale, minZoom);
    // Find screen pixel equivalent once scaled
    offsetX = zoomScale * zoomMidX;
    offsetY = zoomScale * zoomMidY;
    // Find offset to centre, making sure no gap at left or top of holder
    dleft = Math.min(0, $("svg").width() / 2 - offsetX);
    dtop = Math.min(0, $("svg").height() / 2 - offsetY);
    // Make sure no gap at bottom or right of holder
    dleft = Math.max($("svg").width() - w * zoomScale, dleft);
    dtop = Math.max($("svg").height() - h * zoomScale, dtop);
    // set zoom
    svg
        .transition()
        .duration(1000)
        .call(
            zoom.transform,
            d3.zoomIdentity.translate(dleft, dtop).scale(zoomScale)
        );
}

function clicked(d) {
    if (active.node() === this) return reset();
    active.classed("active", false);
    active = d3.select(this).classed("active", true);
    boxZoom(path.bounds(d), path.centroid(d), 50);

    document.getElementById("country-details").style.display = "inline";
}

function reset() {
    active.classed("active", false);
    active = d3.select(null);
    initiateZoom();

    document.getElementById("country-details").style.display = "none";
}

// get map data
//Bind data and create one path per GeoJSON feature
countriesGroup = svg.append("g").attr("id", "map");

// add a background rectangle
countriesGroup
		.append("rect")
		.attr("x", 0)
		.attr("y", 0)
		.attr("width", w)
		.attr("height", h)
		.on("click", reset); // reset when clicking outside countries

// draw a path for each feature/country
countries = countriesGroup
		.selectAll("path")
		.data(countries.features)
		.enter()
		.append("path")
		.attr("d", path)
		.attr("id", function (d) {
				return "country-" + d.id;
		})
		.attr("class", "country")
		.on("click", clicked);
initiateZoom();

