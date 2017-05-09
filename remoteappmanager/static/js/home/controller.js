/*globals: require, console*/
require([
    "home/models",
    "home/views/application_list_view",
    "home/views/application_view",
    "components/vue/dist/vue",
    "gamodule",
    "filters"
], function(
    models,
    application_list_view,
    application_view,
    Vue,
    gamodule) {
    "use strict";

    // This model keeps the retrieved content from the REST query locally.
    // It is only synchronized at initial load.
    var model = new models.ApplicationListModel();

    // Initialize views
    new application_list_view.ApplicationListView({ // jshint ignore:line
        el: '#applist',
        data: function() { return { model: model }; }
    });

    var app_view = new application_view.ApplicationView({
        el: '#appview',
        data: function() { return { model: model }; }
    });

    // Create GA observer
    var ga_observer = new gamodule.GaObserver();

    app_view.$on('start_application', function(application) {
        ga_observer.trigger_application_starting(application.app_data.image.name);
    });

    model.update();
});
