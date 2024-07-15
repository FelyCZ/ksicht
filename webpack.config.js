const path = require('path');
const webpack = require('webpack');
const BundleTracker = require('webpack-bundle-tracker');
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const TerserPlugin = require('terser-webpack-plugin');
const CssMinimizerPlugin = require("css-minimizer-webpack-plugin");

module.exports = (env, argv) => {
    const prodMode = argv.mode === "production";

    return {
        context: __dirname,
        entry: "./assets/js/index",
        output: {
            path: path.resolve("./assets/bundles/"),
            filename: prodMode ? "[name]-[fullhash].js" : "[name].js",
        },

        optimization: {
            minimizer: prodMode
                ? [
                      new TerserPlugin({ parallel: true }),
                      new CssMinimizerPlugin({}),
                  ]
                : [],
        },

        module: {
            rules: [
                {
                    test: /\.js$/,
                    exclude: /node_modules/,
                    use: ["babel-loader"],
                },
                {
                    test: /\.(sa|sc|c)ss$/,
                    use: [
                        MiniCssExtractPlugin.loader,
                        "css-loader",
                        "sass-loader",
                    ],
                },
                {
                    test: /\.(png|jpg|gif)$/,
                    type: "asset/resource",
                    dependency: { not: ["url"] },
                },
                {
                    test: /\.(woff(2)?|ttf|eot|svg)(\?v=\d+\.\d+\.\d+)?$/,
                    type: "asset/resource",
                    dependency: { not: ["url"] },
                },
            ],
        },

        plugins: [
            new MiniCssExtractPlugin({
                // Options similar to the same options in webpackOptions.output
                // both options are optional
                filename: prodMode ? "[name].[contenthash].css" : "[name].css",
                chunkFilename: prodMode ? "[id].[contenthash].css" : "[id].css",
            }),
            new BundleTracker({
                path: __dirname,
                filename: "webpack-stats.json",
            }),
        ],
    };
};
