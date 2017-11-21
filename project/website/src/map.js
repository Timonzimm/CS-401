var d3 = require('d3');
var axios = require('axios');
var $ = require('jquery');
var countries = require('./countries.geo.json');
var science = require('science');
var _ = require('lodash');
var Chartist = require('chartist');
require('materialize-css');

const {
    formatNumber
} = require('./utils.js')

$('#country-details').modal({
    ready: () => details_chart.resizeListener()
});
$('#help-modal').modal();

API_SERVER = "http://127.0.0.1:5000"

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
let details_chart = null;

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

function boxZoom(box, centroid, paddingPerc, callback) {
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
        )
        .on("end", callback);
}

function clicked(d) {
    if (active.node() === this) return reset();
    countries.classed("inactive", true);
    active.classed("active", false);
    active = d3.select(this).classed("active", true);
    active.classed("inactive", false);

    countriesGroup
        .selectAll(".mark")
        .remove()


    boxZoom(path.bounds(d), path.centroid(d), 50, () => {
        axios.all([
                axios.get(`${API_SERVER}/coords/${d.id}`),
                axios.get(`${API_SERVER}/country/${d.id}`),
                axios.get(`${API_SERVER}/attacks/num_victims/${d.id}`),
                axios.get(`${API_SERVER}/attacks/num_attacks/${d.id}`),
                axios.get(`${API_SERVER}/attacks/types/${d.id}/5`),
                axios.get(`${API_SERVER}/attacks/perpetrators/${d.id}/5`),
                axios.get(`${API_SERVER}/attacks/targets/${d.id}/5`)
            ], {
                headers: {
                    'Access-Control-Allow-Origin': '*',
                }
            })
            .then(axios.spread(({
                data: attacks
            }, {
                data: country_infos
            }, {
                data: num_victims
            }, {
                data: num_attacks
            }, {
                data: types
            }, {
                data: groups
            }, {
                data: targets
            }) => {
                // cast, drop undefined and duplicates up to 1 decimal in lat and long or 0 decimal if a lot of attacks
                const points = _.uniqBy(attacks.map(p => [parseFloat(p[0]), parseFloat(p[1])]).filter(p => p[0] && p[1]), p => [p[0].toFixed(1), p[1].toFixed(1)].join());

                const kdeX = science.stats.kde().sample(points.map(p => p[0]))
                const kdeY = science.stats.kde().sample(points.map(p => p[1]))
                const xPDF = kdeX(points.map(p => p[0]))
                const yPDF = kdeY(points.map(p => p[1]))

                let min = Infinity
                let max = 0
                const densities = points.map((p, i) => {
                    const density = xPDF[i][1] * yPDF[i][1]
                    if (density > max) {
                        max = density
                    }
                    if (density < min) {
                        min = density
                    }

                    return p.concat(density)
                }).sort((a, b) => (a[2] > b[2]) ? 1 : -1) // Sort to draw higher density points last, so they are on top

                countriesGroup
                    .selectAll(".mark")
                    .data(densities)
                    .enter()
                    .append("circle")
                    .attr("r", 6 / zoomScale)
                    .attr("class", "mark")
                    .attr("cx", p => projection(p)[0])
                    .attr("cy", p => projection(p)[1])
                    .attr("fill", p => d3.interpolatePlasma((p[2] - min) / (max - min)))

                document.getElementById("country-name").innerText = country_infos[0];
                document.getElementById("country-region").innerText = country_infos[1];
                document.getElementById("country-income").innerText = country_infos[2];
                document.getElementById("country-attacks").innerText = formatNumber(_.sumBy(num_attacks, a => a[1]));
                document.getElementById("country-victims").innerText = formatNumber(_.sumBy(num_victims, v => v[1]));

                document.getElementById("most-common-types").innerHTML = types.map((type, i) => `
                <li class="collection-item">
                    <h3>${formatNumber(type[1])}</h3>
                    <h4>${type[0] === 'Unknown' ? 'Unclassified' : type[0]}</h4>
                </li>`).join("")
                document.getElementById("most-active-groups").innerHTML = groups.map((group, i) => `
                <li class="collection-item">
                    <h3>${formatNumber(group[1])}</h3>
                    <h4>${group[0] === 'Unknown' ? 'Unclaimed' : group[0]}</h4>
                </li>`).join("")
                document.getElementById("most-common-targets").innerHTML = targets.map((target, i) => `
                <li class="collection-item">
                    <h3>${formatNumber(target[1])}</h3>
                    <h4>${target[0] === 'Unknown' ? 'Unclassified' : target[0]}</h4>
                </li>`).join("")

                const data = {
                    labels: num_attacks.map(a => a[0]),
                    series: [
                        num_attacks.map(a => a[1]), // purple/pink=#8f0da4
                        num_victims.map(v => v[1]) // orange
                    ]
                };

                const options = {
                    width: "100%",
                    showArea: true,
                    showPoint: false,
                    axisY: {
                        onlyInteger: true
                    }
                }
                details_chart = new Chartist.Line('#chart-attacks-victims', data, options);
            }))
            .catch((error) => {
                console.log(error);
            });
        document.getElementById("details-menu").style.display = "inline";
    });
}

function reset() {
    active.classed("active", false);
    countries.classed("inactive", false);
    active = d3.select(null);
    initiateZoom();

    countriesGroup
        .selectAll(".mark")
        .remove()

    document.getElementById("details-menu").style.display = "none";
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

console.log("Requesting map...");
// draw a path for each feature/country
axios.get(`${API_SERVER}/attacks/countries`, {
        headers: {
            'Access-Control-Allow-Origin': '*',
        }
    })
    .then((response) => {
        num_attacks = response.data;
        const obj = {}
        let max = 0
        let min = Infinity
        num_attacks.forEach(country => {
            if (country[1] > max) {
                max = country[1]
            }
            if (country[1] < min) {
                min = country[1]
            }

            obj[country[0]] = country[1]
        });

        const interpolator = d3.scaleLinear()
            .range(["#ECF0F1", "#1D1D1D"])
            .interpolate(d3.interpolateLab);

        countries = countriesGroup
            .selectAll("path")
            .data(countries.features)
            .enter()
            .append("path")
            .attr("d", path)
            .attr("fill", (d) => {
                if (obj[d.id])
                    return interpolator(Math.sqrt((obj[d.id] - min) / (max - min)))
                else
                    return "#ECF0F1"
            })
            .attr("id", (d) => `country-${d.id}`)
            .attr("class", "country")
            .on("click", clicked);
    })
    .catch((error) => {
        console.log(error);
    });

initiateZoom();