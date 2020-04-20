"use strict";

const path = require("path");
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

module.exports = {
    plugins: [
        new MiniCssExtractPlugin({filename: "style.css"}),
    ],
    mode: "production",
    // Set debugging source maps to be "inline" for
    // simplicity and ease of use
    devtool: "inline-source-map",

    // The application entry point
    entry: "./src/index.tsx",

    // Where to compile the bundle
    // By default the output directory is `dist`
    output: {
        path: path.resolve(__dirname, "../public"),
        filename: "index.bundle.js"
    },

    // Supported file loaders
    module: {
        rules: [
            {
                test: /\.tsx?$/,
                loader: "ts-loader"
            },
            {
                test: /\.css$/,
                use: [
                    MiniCssExtractPlugin.loader,
                    'css-loader'
                ]
            },
            {
                test: /\.(html|png|jpe?g|gif)$/i,
                loader: 'file-loader',
                options: {
                    name: '[name].[ext]',
                },
            },
        ]
    },

    // File extensions to support resolving
    resolve: {
        extensions: [".ts", ".tsx", ".js"]
    }
};