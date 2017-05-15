"use strict";

var path = require("path");
var components = path.resolve(__dirname, "remoteappmanager/static/components");
var js = path.resolve(__dirname, "remoteappmanager/static/js");

module.exports = {
    entry: {
        // admin: "./remoteappmanager/static/js/admin/main.js",
        user: path.resolve(js, "home/controller.js")
    },
    output: {
        path: path.resolve(__dirname, "remoteappmanager/static/dist"),
        filename: "[name].js"
    },
    resolve: {
        extensions: ["*", ".js"],
        alias: {
            jquery: path.resolve(components, "admin-lte/plugins/jQuery/jquery-2.2.3.min"),
            vuejs: path.resolve(components, "vue/dist/vue.js"),
            // resources: path.resolve(__dirname, "remoteappmanager/jsapi/v1/resources"),

            gamodule: path.resolve(js, "gamodule.js"),
            urlutils: path.resolve(js, "urlutils"),
            utils: path.resolve(js, "utils"),

            filters: path.resolve(js, "vue/filters.js"),
            toolkit: path.resolve(js, "admin/vue-components/toolkit/toolkit.js"),
        }
    },
    externals: {
        resources: "commonjs " + path.resolve(__dirname, "remoteappmanager/jsapi/v1/resources")
    }
}
