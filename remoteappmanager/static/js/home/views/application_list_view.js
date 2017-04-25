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

        props: {
            model: {
                type: Object,
                required: true
            }
        },

        data: function() {
            return {
                loading: true,
                model: { app_list: [], selected_index: null },
                index_mouse_over: null,
                selected_app_callback: function() {}, // Temporary
                stop_application_callback: function() {} // Temporary
            };
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
            },
            stop_application: function(index) {
                this.stop_application_callback(index);
            },
            mouse_enter: function(index) {
                if(this.model.app_list[index].status === 'RUNNING') {
                    this.index_mouse_over = index;
                }
            },
            mouse_leave: function() {
                this.index_mouse_over = null;
            }
        },

        watch: {
            'model.selected_index': function() { this.selected_app_callback(); }
        }
    });

    return {
        ApplicationListView : ApplicationListView
    };
});
