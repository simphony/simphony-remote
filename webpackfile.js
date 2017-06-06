var ExtractTextPlugin = require("extract-text-webpack-plugin");
var path = require("path");
var components = path.resolve(__dirname, "remoteappmanager/static/bower_components");
var js = path.resolve(__dirname, "frontend");

module.exports = {
  // Input files for the bundles of JS/CSS
  entry: {
    admin: path.resolve(js, "admin/main.js"),
    user: path.resolve(js, "user/main.js"),
    sharedDependencies: path.resolve(js, "sharedDependencies")
  },

  // Output bundle of JS
  output: {
    path: path.resolve(__dirname, "remoteappmanager/static/dist"),
    filename: "[name].js"
  },

  // Aliases and file extensions supported
  resolve: {
    extensions: ["*", ".js", ".vue", ".css"],
    alias: {
      lodash: path.resolve(components, "lodash/dist/lodash"),
      jquery: path.resolve(components, "admin-lte/plugins/jQuery/jquery-2.2.3.min"),
      bootstrap: path.resolve(components, "admin-lte/bootstrap/js/bootstrap.min"),
      "bootstrap-css": path.resolve(components, "admin-lte/bootstrap/css/bootstrap.min"),
      "admin-lte": path.resolve(components, "admin-lte/dist/js/app.min"),
      vuejs: path.resolve(components, "vue/dist/vue"),
      "vue-router": path.resolve(components, "vue-router/dist/vue-router"),
      "vue-form": path.resolve(components, "vue-form/dist/vue-form"),

      "admin-resources": path.resolve(js, "admin/admin-resources"),
      "user-resources": path.resolve(js, "user/user-resources"),
      gamodule: path.resolve(js, "gamodule"),
      urlutils: path.resolve(js, "urlutils"),
      utils: path.resolve(js, "utils"),

      filters: path.resolve(js, "vue/filters"),
      ErrorDialog: path.resolve(js, "vue/ErrorDialog"),
      toolkit: path.resolve(js, "vue/toolkit/toolkit"),
    }
  },

  // Loaders for specific file extensions
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
      },
      {
        test: /\.css$/,
        loader: ExtractTextPlugin.extract({ fallback: 'style-loader', use: 'css-loader' })
      },
      {
        test: /\.(eot|svg|ttf|woff|woff2)$/,
        // Output font files
        loader: 'file-loader?name=fonts/[name].[ext]'
      }
    ]
  },

  // Output bundle of CSS
  plugins: [
    new ExtractTextPlugin("[name].css")
  ]
};
