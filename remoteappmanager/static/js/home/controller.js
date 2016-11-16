/*globals: require, console*/
require([
    "jquery", 
    "urlutils", 
    "dialogs",
    "analytics",
    "home/models", 
    "home/views/application_list_view",
    "home/views/application_view",
    "jsapi/v1/resources",
    "handlebars",
    "init"
], function(
    $, 
    urlutils, 
    dialogs, 
    analytics, 
    models, 
    application_list_view,
    application_view, 
    resources,
    hb,
    init) {
    "use strict";

    var ga = analytics.init();
    init.handlebars();

    // This model keeps the retrieved content from the REST query locally.
    // It is only synchronized at initial load.
    var model = new models.ApplicationListModel();
    var app_list_view = new application_list_view.ApplicationListView(model);
    var app_view = new application_view.ApplicationView(model);

    app_list_view.entry_clicked = function (index) {
        model.selected_index = index;
        app_list_view.update_selected();
        app_view.render(false, 200);
    };
    
    app_list_view.stop_button_clicked = function(index) {
        if (model.status[index] === models.Status.STOPPING) {
            return;
        }
        model.status[index] = models.Status.STOPPING;
        
        var app_info = model.app_data[index];
        var url_id = app_info.container.url_id;

        app_list_view.update_entry(index);
        
        resources.Container.delete(url_id)
            .done(function () {
                model.update_idx(index)
                    .done(function() {
                        app_list_view.update_entry(index);
                        app_view.render(true);
                    })
                    .fail(function(error) {
                        model.status[index] = models.Status.STOPPED;
                        app_list_view.update_entry(index);
                        app_view.render(true);
                        dialogs.webapi_error_dialog(error);
                    });
                })
            .fail(
                function (error) {
                    model.status[index] = models.Status.STOPPED;
                    app_list_view.update_entry(index);
                    app_view.render(true);
                    dialogs.webapi_error_dialog(error);
                });
    };

    app_view.start_button_clicked = function (index) {
        // The container is not running. This is a start button.
        var mapping_id = model.app_data[index].mapping_id;
        var image_name = model.app_data[index].image.name;

        if (model.status[index] === models.Status.STARTING) {
            return;
        }
        
        model.status[index] = models.Status.STARTING;
        app_view.render(false, null);
        app_list_view.update_entry(index);

        var configurables_data = {};
        var configurables = model.configurables[index];
        configurables_data = {};

        Object.getOwnPropertyNames(configurables).forEach(
            function(val, idx, array) {   // jshint ignore:line
                var configurable = configurables[val];
                var tag = configurable.tag;
                configurables_data[tag] = configurable.as_config_dict();
            }
        );
       
        resources.Container.create({
            mapping_id: mapping_id,
            configurables: configurables_data
        }).done(function() {
            ga("send", "event", {
                eventCategory: "Application",
                eventAction: "start",
                eventLabel: image_name
            });

            model.update_idx(index)
                .always(function() {
                    app_list_view.update_entry(index);
                    app_list_view.update_selected();
                    app_view.render(true, 200);
                })
                .fail(function(error) {
                    model.status[index] = models.Status.STOPPED;
                    app_list_view.update_entry(index);
                    app_view.render(true, 200);
                    dialogs.webapi_error_dialog(error);
                });
        }).fail(function(error) {
            model.status[index] = models.Status.STOPPED;
            app_list_view.update_entry(index);
            app_list_view.update_selected();
            app_view.render(true, 200);
            dialogs.webapi_error_dialog(error);
        });
    };

    $.when(model.update()).done(function () { 
        app_list_view.render();
        app_view.render(false, 200);
    });

});
