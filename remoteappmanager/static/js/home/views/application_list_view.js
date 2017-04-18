define([
    'urlutils',
    '../components/vue/dist/vue'
], function (urlutils) {
    'use strict';

    /* Create application_list ViewModel
    (will next be wrapped in a main ViewModel which will contain the
    applicationListView and the applicationView) */
    var applicationListView = new Vue({
        el: '#applist',

        data: {
            loading: true,
            application_list: [],
            selected_app: null
        },

        methods: {
            get_icon_src: function(app_data) {
                var icon_data = app_data.image.icon_128;
                return (
                    icon_data ?
                    'data:image/png;base64,' + icon_data :
                    urlutils.path_join(
                        this.base_url, 'static', 'images', 'generic_appicon_128.png'
                    )
                );
            },
            get_app_name: function(app_data) {
                return (
                    app_data.image.ui_name ?
                    app_data.image.ui_name :
                    app_data.image.name
                );
            }
        }
    });

    return {
        applicationListView : applicationListView
    };
});
