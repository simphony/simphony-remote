define([
    'urlutils',
    'utils',
    "dialogs",
    '../../components/vue/dist/vue.min',
    "jsapi/v1/resources"
], function (urlutils, utils, dialogs, Vue, resources) {
    'use strict';

    var Status = utils.Status;

    /* Create application_list ViewModel
    (will next be wrapped in a main ViewModel which will contain the
    applicationListView and the applicationView) */
    var ApplicationListView = Vue.extend({
        el: '#applist',

        data: function() {
            return {
                loading: true,
                model: { app_list: [], selected_index: null },
                selected_app_callback: function() {} // Temporary
            };
        },

        methods: {
            stop_application: function(index) {
                var app_stopping = this.model.app_list[index];
                app_stopping.status = Status.STOPPING;

                var url_id = app_stopping.app_data.container.url_id;

                resources.Container.delete(url_id)
                .done(function() {
                    this.model.update_idx(index)
                    .fail(function(error) {
                        app_stopping.status = Status.STOPPED;
                        dialogs.webapi_error_dialog(error);
                    });
                }.bind(this))
                .fail(function(error) {
                    app_stopping.status = Status.STOPPED;
                    dialogs.webapi_error_dialog(error);
                });
            }
        },

        filters: utils.filters
    });

    return {
        ApplicationListView : ApplicationListView
    };
});
