define([
    "components/vue/dist/vue",
    "urlutils"
], function (Vue, urlUtils) {
    'use strict';

    Vue.filter('iconSrc', function(icon_data) {
        return (
            icon_data ?
            'data:image/png;base64,' + icon_data :
            urlUtils.path_join(
                window.apidata.base_url, 'static', 'images', 'generic_appicon_128.png'
            )
        );
    });

    Vue.filter('appName', function(image) {
        return image.ui_name? image.ui_name: image.name;
    });

    return null;
});
