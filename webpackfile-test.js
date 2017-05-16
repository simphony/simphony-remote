var path = require("path");
var jstests = path.resolve(__dirname, "jstests");
var components = path.resolve(__dirname, "remoteappmanager/static/bower_components");
var js = path.resolve(__dirname, "remoteappmanager/static/js");

module.exports = {
    entry: {
        testsuite: path.resolve(jstests, "testsuite.js")
    },

    output: {
        path: path.resolve(jstests, "dist"),
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

            "user-resources": path.resolve(jstests, "tests/user/mock_jsapi"),
            gamodule: path.resolve(js, "gamodule"),
            urlutils: path.resolve(js, "urlutils"),
            utils: path.resolve(js, "utils"),

            filters: path.resolve(js, "vue/filters"),
            toolkit: path.resolve(js, "vue/toolkit/toolkit"),
            "toolkit-dir": path.resolve(js, "vue/toolkit"),

            helpers: path.resolve(jstests, "helpers"),

            admin: path.resolve(js, "admin"),
            user: path.resolve(js, "user"),
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
