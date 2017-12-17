var debug = process.env.NODE_ENV !== 'production';
var webpack = require('webpack');
const Uglify = require("uglifyjs-webpack-plugin");
const CompressionPlugin = require('compression-webpack-plugin');



module.exports = {
    context: __dirname,
    devtool: debug ? "inline-sourcemap" : null,
    entry: "./src/map.js",
    output: {
        path: __dirname + "/static",
        filename: "bundle.js"
    },
    plugins: [
	new webpack.DefinePlugin({
	      "process.env": {
		NODE_ENV: JSON.stringify("production")
	      }
	    }),
	    new webpack.optimize.OccurrenceOrderPlugin(),
            new webpack.optimize.DedupePlugin(),
	    new Uglify({
	      mangle: true,
	      compress: {
		warnings: false, // Suppress uglification warnings
		pure_getters: true,
		unsafe: true,
		unsafe_comps: true,
		screw_ie8: true
	      },
	      output: {
		comments: false,
	      },
	      exclude: [/\.min\.js$/gi] // skip pre-minified libs
	    }),
	    new webpack.optimize.AggressiveMergingPlugin(),
	    //new BundleAnalyzerPlugin(),
	    new webpack.IgnorePlugin(/^\.\/locale$/, /moment$/),
	    new webpack.NoEmitOnErrorsPlugin(),
	    new CompressionPlugin({
	      asset: "[path].gz[query]",
	      algorithm: "gzip",
	      test: /\.js$/,
	      threshold: 10240,
	      minRatio: 0.8
	    }),
    ],
};
