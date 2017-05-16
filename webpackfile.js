var path = require("path");
var components = path.resolve(__dirname, "remoteappmanager/static/bower_components");
var js = path.resolve(__dirname, "remoteappmanager/static/js");

module.exports = {
    entry: {
        admin: path.resolve(js, "admin/main.js"),
        user: path.resolve(js, "home/main.js")
    },

    output: {
        path: path.resolve(__dirname, "remoteappmanager/static/dist"),
        filename: "[name].js"
    },

    resolve: {
        extensions: ["*", ".js"],
        alias: {
            lodash: path.resolve(components, "lodash/dist/lodash"),
            jquery: path.resolve(components, "admin-lte/plugins/jQuery/jquery-2.2.3.min"),
            vuejs: path.resolve(components, "vue/dist/vue"),
            "vue-router": path.resolve(components, "vue-router/dist/vue-router"),
            "vue-form": path.resolve(components, "vue-form/dist/vue-form"),

            "admin-resources": path.resolve(js, "admin/admin-resources"),
            "home-resources": path.resolve(js, "home/home-resources"),
            gamodule: path.resolve(js, "gamodule"),
            urlutils: path.resolve(js, "urlutils"),
            utils: path.resolve(js, "utils"),

            filters: path.resolve(js, "vue/filters"),
            toolkit: path.resolve(js, "admin/vue-components/toolkit/toolkit"),
        }
    },

    module: {
        rules: [
            {
                test: /\.js$/,
                exclude: /(node_modules|bower_components)/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        presets: ['env']
                    }
                }
            }
        ]
    }
}
