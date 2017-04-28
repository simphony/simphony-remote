/*globals: require, console*/
require([
    "home/models",
    "home/views/application_list_view",
    "home/views/application_view"
], function(
    models,
    application_list_view,
    application_view) {
    "use strict";

    // This model keeps the retrieved content from the REST query locally.
    // It is only synchronized at initial load.
    var model = new models.ApplicationListModel();

    new application_list_view.ApplicationListView({ // jshint ignore:line
        el: '#applist',
        data: function() { return { model: model }; }
    });

    new application_view.ApplicationView({ // jshint ignore:line
        el: '#appview',
        data: function() { return { model: model }; }
    });

    model.update();
});
