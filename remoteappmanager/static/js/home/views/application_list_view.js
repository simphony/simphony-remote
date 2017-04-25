define([
    'urlutils',
    '../../components/vue/dist/vue.min'
], function (urlutils, Vue) {
    'use strict';

    /* Create application_list ViewModel
    (will next be wrapped in a main ViewModel which will contain the
    applicationListView and the applicationView) */
    var ApplicationListView = Vue.extend({
        el: '#applist',

        data: function() {
            return {
                loading: true,
                model: { app_list: [], selected_index: null },
                selected_app_callback: function() {}, // Temporary
                stop_application_callback: function() {} // Temporary
            };
        },

        methods: {
            stop_application: function(index) {
                this.stop_application_callback(index);
            }
        },

        filters: {
            icon_src: function(icon_data) {
                return (
                    icon_data ?
                    'data:image/png;base64,' + icon_data :
                    urlutils.path_join(
                        window.apidata.base_url, 'static', 'images', 'generic_appicon_128.png'
                    )
                );
            },
            app_name: function(image) {
                return image.ui_name? image.ui_name: image.name;
            }
        }
    });

    return {
        ApplicationListView : ApplicationListView
    };
});
