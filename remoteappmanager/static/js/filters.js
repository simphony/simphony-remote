define([
    "urlutils",
    "components/vue/dist/vue"
], function(urlutils, Vue) {
    "use strict";

    Vue.filter('icon_src', function(icon_data) {
        return (
            icon_data ?
            'data:image/png;base64,' + icon_data :
            urlutils.path_join(
                window.apidata.base_url, 'static', 'images', 'generic_appicon_128.png'
            )
        );
    });

    Vue.filter('app_name', function(image) {
        return image.ui_name? image.ui_name: image.name;
    });

    return null;
});