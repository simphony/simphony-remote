/*globals: require, console*/
require([
    "home/models",
    "home/views/application_list_view",
    "home/views/application_view",
    "components/vue/dist/vue.min",
    "gamodule",
    "utils"
], function(
    models,
    application_list_view,
    application_view,
    Vue,
    gamodule,
    utils) {
    "use strict";

    var Status = utils.Status;

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
    Vue.filter('is_starting', function(application) {
        return application.status === Status.STARTING;
    });
    Vue.filter('is_running', function(application) {
        return application.status === Status.RUNNING;
    });
    Vue.filter('is_stopping', function(application) {
        return application.status === Status.STOPPING;
    });
    Vue.filter('is_stopped', function(application) {
        return application.status === Status.STOPPED;
    });

    // This model keeps the retrieved content from the REST query locally.
    // It is only synchronized at initial load.
    var model = new models.ApplicationListModel();

    // Initialize views
    new application_list_view.ApplicationListView({ // jshint ignore:line
        el: '#applist',
        data: function() { return { model: model }; }
    });

    new application_view.ApplicationView({ // jshint ignore:line
        el: 'div.content-wrapper',
        data: function() { return { model: model }; }
    });

    // Create GA Vue object
    new gamodule.GaView({ // jshint ignore:line
        data: function() { return { model: model }; }
    });

    model.update();
});
