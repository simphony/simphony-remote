/*globals: require, console*/
require([
    "home/models",
    "home/views/application_list_view",
    "home/views/application_view",
    "components/vue/dist/vue",
    "gamodule",
    "vue/filters"
], function(
    models,
    applicationListView,
    applicationView,
    Vue,
    gamodule) {
    "use strict";

    // This model keeps the retrieved content from the REST query locally.
    // It is only synchronized at initial load.
    var model = new models.ApplicationListModel();

    // Initialize views
    var appListView = new applicationListView.ApplicationListView({
        el: '#applist',
        data: function() { return { model: model }; }
    });

    var appView = new applicationView.ApplicationView({
        el: '#appview',
        data: function() { return { model: model }; }
    });

    // Create GA observer
    var gaObserver = new gamodule.GaObserver();

    appView.$on('start_application', function(application) {
        gaObserver.trigger_application_starting(application.app_data.image.name);
    });

    appListView.$on('entry_clicked', function() { appView.focus_iframe(); });

    model.update();
});
