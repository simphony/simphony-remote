var path = require("path");
var tests = path.resolve(__dirname, "frontend/tests");
var js = path.resolve(__dirname, "frontend");

module.exports = {
  entry: {
    testsuite: path.resolve(tests, "testsuite.js")
  },

  output: {
    path: path.resolve(tests, "dist"),
    filename: "[name].js"
  },

  resolve: {
    extensions: ["*", ".js", ".vue"],
    alias: {
      vue: "vue/dist/vue",
      "vue-router": "vue-router/dist/vue-router",

      "user-resources": path.resolve(tests, "tests/user/mock_jsapi"),
      gamodule: path.resolve(js, "gamodule"),
      urlutils: path.resolve(js, "urlutils"),
      utils: path.resolve(js, "utils"),

      toolkit: path.resolve(js, "toolkit/toolkit"),

      helpers: path.resolve(tests, "helpers"),

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
          loader: 'babel-loader'
        }
      },
      {
        test: /\.vue$/,
        use: {
          loader: 'vue-loader'
        }
      }
    ]
  }
};
