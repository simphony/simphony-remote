/*globals: require, console*/
require([
    "jquery", 
    "urlutils", 
    "dialogs",
    "remoteappapi", 
    "analytics",
    "home/models", 
    "home/views"
], function($, urlutils, dialogs, RemoteAppAPI, analytics, models, views) {
    "use strict";

    var ga = analytics.init();
    var base_url = window.apidata.base_url;
    var appapi = new RemoteAppAPI(base_url);
   
    // This model keeps the retrieved content from the REST query locally.
    // It is only synchronized at initial load.
    var model = new models.ApplicationListModel(appapi);
    var view = new views.ApplicationListView(model);
    
    var new_container_window = function (url_id) {
        // Opens a new window for the container at url_id
        var w = window.open(undefined);
        if (w !== undefined) {
            w.location = urlutils.path_join(
                base_url,
                "containers",
                url_id
            );
        }
    };

    view.view_button_clicked = function (index) {
        var promise = $.Deferred();
        var app_info = model.app_data[index];
        new_container_window(app_info.container.url_id);
        promise.resolve();
        return promise;
    };
    
    view.stop_button_clicked = function (index) {
        var promise = $.Deferred();
        var app_info = model.app_data[index];

        var url_id = app_info.container.url_id;
        
        appapi.stop_application(url_id, {
            success: function () {
                model.update_idx(index)
                    .done(promise.resolve)
                    .fail(promise.reject);
            },
            error: function (jqXHR, status, error) {
                dialogs.ajax_error_dialog(jqXHR, status, error);
                promise.reject();
            }});
        return promise;
    };
        
    view.start_button_clicked = function (index) {
        // The container is not running. This is a start button.
        var mapping_id = model.app_data[index].mapping_id;
        var image_name = model.app_data[index].image.name;
        
        var configurables_data = {};
        var configurables = model.configurables[index];
        configurables_data = {};

        Object.getOwnPropertyNames(configurables).forEach(
            function(val, idx, array) {
                var configurable = configurables[val];
                var tag = configurable.tag;
                configurables_data[tag] = configurable.as_config_dict();
            }
        );
       
        var promise = $.Deferred();
        appapi.start_application(mapping_id, configurables_data, {
            error: function(jqXHR, status, error) {
                promise.reject();
            },
            statusCode: {
                201: function (data, textStatus, request) {
                    var location = request.getResponseHeader('Location');
                    var url = urlutils.parse(location);
                    var arr = url.pathname.replace(/\/$/, "").split('/');
                    var url_id = arr[arr.length-1];
                    
                    ga("send", "event", {
                        eventCategory: "Application",
                        eventAction: "start",
                        eventLabel: image_name
                    });
                    
                    new_container_window(url_id);
                    model.update_idx(index).done(promise.resolve);
                }
            }
        });
        
        return promise;
    };

    $.when(model.update()).done(function () { view.render(); });

});
