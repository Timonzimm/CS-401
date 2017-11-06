var svg = d3.select("svg"),
    width = +svg.attr("width"),
    height = +svg.attr("height"),
    active = d3.select(null);

var projection = d3.geoMercator()
    .scale((width - 3) / (2 * Math.PI))
    .translate([width / 2, height / 2]);

var path = d3.geoPath().projection(projection);

var graticule = d3.geoGraticule();

svg.append("defs").append("path")
    .datum({
        type: "Sphere"
    })
    .attr("id", "sphere")
    .attr("d", path);

svg.append("use")
    .attr("class", "stroke")
    .attr("xlink:href", "#sphere");

svg.append("use")
    .attr("class", "fill")
    .attr("xlink:href", "#sphere");

svg.append("path")
    .datum(graticule)
    .attr("class", "graticule")
    .attr("d", path);

d3.json("https://unpkg.com/world-atlas@1/world/50m.json", function (error, world) {
    if (error) throw error;

    svg.insert("path", ".graticule")
        .datum(topojson.feature(world, world.objects.land))
        .attr("class", "land")
        .attr("d", path)
        .on("click", clicked);

    svg.insert("path", ".graticule")
        .datum(topojson.mesh(world, world.objects.countries, function (a, b) {
            return a !== b;
        }))
        .attr("class", "boundary")
        .attr("d", path);
})

var zoom = d3.zoom()
    .translate([0, 0])
    .scale(1)
    .scaleExtent([1, 8])
    .on("zoom", zoomed);

function clicked(d) {
    if (active.node() === this) return reset();
    active.classed("active", false);
    active = d3.select(this).classed("active", true);

    var bounds = path.bounds(d),
        dx = bounds[1][0] - bounds[0][0],
        dy = bounds[1][1] - bounds[0][1],
        x = (bounds[0][0] + bounds[1][0]) / 2,
        y = (bounds[0][1] + bounds[1][1]) / 2,
        scale = .9 / Math.max(dx / width, dy / height),
        translate = [width / 2 - scale * x, height / 2 - scale * y];

    svg.transition()
        .duration(750)
        .call(zoom.translate(translate).scale(scale).event);
}