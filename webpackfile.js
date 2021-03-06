var ExtractTextPlugin = require("extract-text-webpack-plugin");
var path = require("path");
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
      // CSS
      "bootstrap-css": "admin-lte/bootstrap/css/bootstrap.min",
      "font-awesome-css": "font-awesome/css/font-awesome.min",
      "ionicons-css": "ionicons/dist/css/ionicons.min",
      "admin-lte-css": "admin-lte/dist/css/AdminLTE.min",
      "skin-black-css": "admin-lte/dist/css/skins/skin-black.min",
      "skin-red-css": "admin-lte/dist/css/skins/skin-red.min",
      "skin-blue-css": "admin-lte/dist/css/skins/skin-blue.min",

      // JS
      jquery: "admin-lte/plugins/jQuery/jquery-2.2.3.min",
      bootstrap: "admin-lte/bootstrap/js/bootstrap.min",
      vue: "vue/dist/vue.min",
      "vue-router": "vue-router/dist/vue-router",

      "admin-resources": path.resolve(js, "admin/admin-resources"),
      "user-resources": path.resolve(js, "user/user-resources"),
      gamodule: path.resolve(js, "gamodule"),
      urlutils: path.resolve(js, "urlutils"),
      utils: path.resolve(js, "utils"),

      toolkit: path.resolve(js, "toolkit/toolkit"),
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
        test: /\.(eot|svg|ttf|woff|woff2|jpg)$/,
        // Output font files
        loader: 'file-loader?name=files/[name].[ext]'
      }
    ]
  },

  // Output bundle of CSS
  plugins: [
    new ExtractTextPlugin("[name].css")
  ]
};
