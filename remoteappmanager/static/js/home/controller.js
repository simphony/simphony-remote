/*globals: require, console*/
require([
    "home/models",
    "home/views/application_list_view",
    "home/views/application_view",
    "components/vue/dist/vue.min",
    "gamodule",
    'urlutils'
], function(
    models,
    application_list_view,
    application_view,
    Vue,
    gamodule,
    urlutils) {
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
