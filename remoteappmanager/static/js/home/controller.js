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

    /*
    // Temporary solution, when ApplicationView will be a Vue Object the render
    // will be automatically triggered
    app_list_view.stop_application_callback = function(index) {
        if (model.app_list[index].status === Status.STOPPING) {
            return;
        }
        model.app_list[index].status = Status.STOPPING;

        var app_info = model.app_list[index].app_data;
        var url_id = app_info.container.url_id;

        resources.Container.delete(url_id)
            .done(function () {
                model.update_idx(index)
                    .done(function() {
                        app_view.render(true);
                    })
                    .fail(function(error) {
                        model.app_list[index].status = Status.STOPPED;
                        app_view.render(true);
                        dialogs.webapi_error_dialog(error);
                    });
                })
            .fail(
                function (error) {
                    model.app_list[index].status = Status.STOPPED;
                    app_view.render(true);
                    dialogs.webapi_error_dialog(error);
                });
    };*/

    $.when(model.update()).done(function () {
        app_list_view.loading = false;

        app_list_view.model = model;
        app_view.model = model;

        //app_view.render(false, 200);
    });

});
