define([
    'urlutils',
    'utils',
    '../../components/vue/dist/vue.min'
], function (urlutils, utils, Vue) {
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

        filters: utils.filters
    });

    return {
        ApplicationListView : ApplicationListView
    };
});
