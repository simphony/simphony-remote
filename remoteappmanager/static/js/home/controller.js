/*globals: require, console*/
require([
    "urlutils",
    "home/models",
    "home/views/application_list_view",
    "home/views/application_view"
], function(
    urlutils,
    models,
    application_list_view,
    application_view) {
    "use strict";

    // This model keeps the retrieved content from the REST query locally.
    // It is only synchronized at initial load.
    var model = new models.ApplicationListModel();

    var app_list_view = new application_list_view.ApplicationListView();
    var app_view = new application_view.ApplicationView();

    $.when(model.update()).done(function () {
        app_list_view.model = model;
        app_view.model = model;
    });
});
