let Vue = require("vuejs");
let urlUtils = require("urlutils");

Vue.filter('iconSrc', function(icon_data) {
  return (
    icon_data ?
    'data:image/png;base64,' + icon_data :
    urlUtils.pathJoin(
      window.apidata.base_url, 'static', 'images', 'generic_appicon_128.png'
    )
  );
});

Vue.filter('appName', function(image) {
  return image.ui_name? image.ui_name: image.name;
});

Vue.filter('appUrl', function(app) {
  return urlUtils.pathJoin(
    window.apidata.base_url,
    'containers',
    app.appData.container.url_id
  );
});
