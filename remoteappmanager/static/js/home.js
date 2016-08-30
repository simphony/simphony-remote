/*globals: require, console*/
require(
    ["jquery", "jhapi", "utils", "remoteappapi"],
    function($, JHAPI, utils, RemoteAppAPI) {
        "use strict";
    
        var base_url = window.apidata.base_url;
        var user = window.apidata.user;
        var api = new JHAPI(base_url);
        var appapi = new RemoteAppAPI(base_url);
        
        var report_error = function (jqXHR, status, error) {
            var msg = utils.log_ajax_error(jqXHR, status, error);
            $(".spawn-error-msg").text(msg).show();
        };

        var render_applist_entry = function (info) {
            // Adds the retrieved information to the DOM for a single entry.
            var html = '<div class="row">';
            html += '<img src="'+utils.url_path_join(
                        base_url, "static","images","generic_appicon_128.png")+
                    '" class="col-sm-2 va" />';
            html += '<div class="col-sm-7 va"><h4>'+info.image.ui_name+'</h4></div>';
            html += '<div">';
            if (info.container === null) {
                html += '<div class="col-sm-2 va">';
                html += '<button id="'+info.mapping_id+'" name="action" value="start" class="start-button btn btn-primary"><i class="fa fa-spinner fa-spin" aria-hidden="true" style="display: none"></i> Start</button>';
                html += '</div>';
            } else {
                html += '<div class="col-sm-1 va">';
                html += '<button id="'+info.container.url_id+'" name="action" value="view" class="view-button btn btn-success">View</button>';
                html += '</div>';
                html += '<div class="col-sm-1 va">';
                html += '<button id="'+info.container.url_id+'" name="action" value="stop" class="stop-button btn btn-danger"><i class="fa fa-spinner fa-spin" aria-hidden="true" style="display: none"></i> Stop</button>';
                html += '</div>';
            }
            html += '</div>';
            html += '</div>';
            return html;
        };
        
        var render_applist = function (promises) {
            var html = "";
            for (var i = 0; i < promises.length; i++) {
                var result = promises[i];
                if (result[2].status === 200) {
                    var info = result[0];
                    html += render_applist_entry(info);
                }
            }
            $("#applist").html(html);
        };
      
        var request_single_app_infos = function (response) {
            var requests = [];
            
            for (var i = 0; i < response.items.length; i++) {
                requests.push(appapi.application_info(response.items[i]));
            }
            
            utils.all(requests)
                .always(render_applist)
                .done(register_button_eventhandlers);
        };
        
        var register_button_eventhandlers = function () {
            // Registers the event handlers on the buttons after addition
            // of the new entries to the list.
            $("#stop").click(function () {
                api.stop_server(user, {
                    success: function () {
                        $("#stop").hide();
                    }
                });
            });

            $(".start-button").click(function () {
                    var button = this;
                    var id = button.id;
                    $(button).find(".fa-spinner").show();

                    appapi.start_application(id, {
                        error: function(jqXHR, status, error) {
                            report_error(jqXHR, status, error);
                            $(button).find(".fa-spinner").hide();
                        },
                        statusCode: {
                            201: function (data, textStatus, request) {
                                var location = request.getResponseHeader('Location');
                                var url = utils.parse_url(location);
                                var arr = url.pathname.replace(/\/$/, "").split('/');
                                var id = arr[arr.length-1];
                                $(button).find(".fa-spinner").hide();

                                window.location = utils.url_path_join(
                                    base_url,
                                    "containers",
                                    id
                                );
                            }
                        }
                    });
                }
            );

            $(".view-button").click(function () {
                    var id = this.id;
                    window.location = utils.url_path_join(base_url, "containers", id);
                }
            );

            $(".stop-button").click(function () {
                var button = this;
                var id = this.id;
                $(button).find(".fa-spinner").show();
                appapi.stop_application(id, {
                    success: function () {
                        $(button).find(".fa-spinner").hide();
                        window.location.reload();
                    },
                    error: function (jqXHR, status, error) {
                        report_error(jqXHR, status, error);
                        $(button).find(".fa-spinner").hide();
                    }
                });
            });
        };
        
        $.when(appapi.available_applications()).done(request_single_app_infos);

    }
);
