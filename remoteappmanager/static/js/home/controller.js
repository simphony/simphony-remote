/*globals: require, console*/
require([
    "home/models",
    "home/views/application_list_view",
    "home/views/application_view",
    "gamodule"
], function(
    models,
    application_list_view,
    application_view,
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
