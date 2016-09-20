/*globals: require, console*/
require(
    ["jquery", "jhapi", "utils", "remoteappapi", "home/models", "home/views"],
    function($, JHAPI, utils, RemoteAppAPI, models, views) {
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

        view.x_button_clicked = function () {
            // Triggered when the button X (left side) is clicked
            var button = this;
            var index = $(button).data("index");
            $(button).find(".fa-spinner").show();
            var app_info = model.data[index];

            if (app_info.container !== null) {
                // The container is already running, this is a View button
                window.location = utils.url_path_join(
                    base_url, 
                    "containers", 
                    app_info.container.url_id);
            } else {
                // The container is not running. This is a start button. 
                var mapping_id = model.data[index].mapping_id;
                appapi.start_application(mapping_id, {
                    error: function(jqXHR, status, error) {
                        report_error(jqXHR, status, error);
                        $(button).find(".fa-spinner").hide();
                    },
                    statusCode: {
                        201: function (data, textStatus, request) {
                            var location = request.getResponseHeader('Location');
                            var url = utils.parse_url(location);
                            var arr = url.pathname.replace(/\/$/, "").split('/');
                            var url_id = arr[arr.length-1];
                            $(button).find(".fa-spinner").hide();

                            window.location = utils.url_path_join(
                                base_url,
                                "containers",
                                url_id
                            );
                        }
                    }
                });
            }
        };

        view.y_button_clicked = function () {
            // Triggered when the button Y (right side) is clicked
            var button = this;
            var index = $(button).data("index");
            $(button).find(".fa-spinner").show();
            var app_info = model.data[index];

            var url_id = app_info.container.url_id;
            appapi.stop_application(url_id, {
                success: function () {
                    $(button).find(".fa-spinner").hide();
                    view.reset_buttons_to_start(index);
                    app_info.container = null;
                },
                error: function (jqXHR, status, error) {
                    report_error(jqXHR, status, error);
                    $(button).find(".fa-spinner").hide();
                }
            });
        };
       
        $.when(model.update()).done(function () { view.render(); });

    }
);
