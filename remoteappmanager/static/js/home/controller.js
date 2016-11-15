/*globals: require, console*/
require([
    "jquery", 
    "urlutils", 
    "dialogs",
    "analytics",
    "home/models", 
    "home/views/application_list_view",
    "jsapi/v1/resources"
], function($, urlutils, dialogs, analytics, models, application_list_view, resources) {
    "use strict";

    var ga = analytics.init();

    // This model keeps the retrieved content from the REST query locally.
    // It is only synchronized at initial load.
    var model = new models.ApplicationListModel();
    var view = new application_list_view.ApplicationListView(model);
    
    view.stop_button_clicked = function (index) {
        var promise = $.Deferred();
        var app_info = model.app_data[index];

        var url_id = app_info.container.url_id;
        
        resources.Container.delete(url_id)
            .done(function () {
                model.update_idx(index)
                    .done(promise.resolve)
                    .fail(promise.reject);
                })
            .fail(
                function (error) {
                    dialogs.webapi_error_dialog(error);
                    promise.reject();
                });
                
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
            function(val, idx, array) {  // jshint ignore:line
                var configurable = configurables[val];
                var tag = configurable.tag;
                configurables_data[tag] = configurable.as_config_dict();
            }
        );
       
        var promise = $.Deferred();
        
        resources.Container.create({
            mapping_id: mapping_id,
            configurables: configurables_data
        }).done(function() {
            ga("send", "event", {
                eventCategory: "Application",
                eventAction: "start",
                eventLabel: image_name
            });

            model.update_idx(index).done(promise.resolve);
        }).fail(function() { promise.reject(); });
        
        return promise;
    };

    $.when(model.update()).done(function () { view.render(); });

});
