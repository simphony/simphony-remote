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
            vuejs: path.resolve(components, "vue/dist/vue"),

            resources: path.resolve(js, "resources"),
            gamodule: path.resolve(js, "gamodule"),
            urlutils: path.resolve(js, "urlutils"),
            utils: path.resolve(js, "utils"),

            filters: path.resolve(js, "vue/filters"),
            toolkit: path.resolve(js, "admin/vue-components/toolkit/toolkit"),
        }
    }
}
