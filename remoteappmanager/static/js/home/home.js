/*globals: require, console*/
require(
    ["jquery", "utils", "remoteappapi", "home/models", "home/views"],
    function($, utils, RemoteAppAPI, models, views) {
        "use strict";
    
        var base_url = window.apidata.base_url;
        var appapi = new RemoteAppAPI(base_url);
       
        // This model keeps the retrieved content from the REST query locally.
        // It is only synchronized at initial load.
        var model = new models.ApplicationListModel(appapi);
        var view = new views.ApplicationListView(model);
        
        var report_error = function (jqXHR, status, error) {
            // Writes an error message resulting from an incorrect
            // ajax operation. Parameters are from the resulting ajax.
            var msg = utils.log_ajax_error(jqXHR, status, error);
            $(".spawn-error-msg").text(msg).show();
        };

        view.view_button_clicked = function (index) {
            var app_info = model.data[index];

            window.location = utils.url_path_join(
                base_url,
                "containers",
                app_info.container.url_id);
        };
        
        view.stop_button_clicked = function (index) {
            var app_info = model.data[index];

            var url_id = app_info.container.url_id;
            return appapi.stop_application(url_id, {
                success: function () {
                    view.reset_buttons_to_start(index);
                    app_info.container = null;
                },
                error: function (jqXHR, status, error) {
                    report_error(jqXHR, status, error);
                }});
        };
            
        view.start_button_clicked = function (index) {
            // The container is not running. This is a start button.
            var mapping_id = model.data[index].mapping_id;
            return appapi.start_application(mapping_id, {
                error: function(jqXHR, status, error) {
                    report_error(jqXHR, status, error);
                },
                statusCode: {
                    201: function (data, textStatus, request) {
                        var location = request.getResponseHeader('Location');
                        var url = utils.parse_url(location);
                        var arr = url.pathname.replace(/\/$/, "").split('/');
                        var url_id = arr[arr.length-1];

                        window.location = utils.url_path_join(
                            base_url,
                            "containers",
                            url_id
                        );
                    }
                }
            });
        };

        $.when(model.update()).done(function () { view.render(); });

    }
);