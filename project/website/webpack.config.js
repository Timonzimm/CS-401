var debug = process.env.NODE_ENV !== 'production';
var webpack = require('webpack');

module.exports = {
    context: __dirname,
    devtool: debug ? "inline-sourcemap" : null,
    entry: "./src/map.js",
    output: {
        path: __dirname + "/static",
        filename: "bundle.js"
    },
    plugins: debug ? [] : [
        new webpack.optimize.DedupePlugin(),
        new webpack.optimize.OccurenceOrderPlugin(),
    ],
};