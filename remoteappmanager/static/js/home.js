/*globals: require, console*/
require(
    ["jquery", "jhapi", "utils", "remoteappapi"],
    function($, JHAPI, utils, RemoteAppAPI) {
        "use strict";
    
        var base_url = window.apidata.base_url;
        var appapi = new RemoteAppAPI(base_url);
       
        // This model keeps the retrieved content from the REST query locally.
        // It is only synchronized at initial load.
        var application_model = [];
        
        var report_error = function (jqXHR, status, error) {
            // Writes an error message resulting from an incorrect
            // ajax operation. Parameters are from the resulting ajax.
            var msg = utils.log_ajax_error(jqXHR, status, error);
            $(".spawn-error-msg").text(msg).show();
        };

        var render_applist_entry = function (index, info) {
            // Returns a HTML snippet for a single application entry
            // index: 
            //     a progressive index for the entry.
            // info:
            //     A dictionary containing the retrieved data about the application
            //     and (possibly) the container.
            var html = '<div class="row">';
            
            if (info.image.icon_128 === '') {
                html += '<img src="' + utils.url_path_join(
                        base_url, "static", "images", "generic_appicon_128.png") +
                    '" class="col-sm-2 va" />';
            } else {
                html += '<img src="data:image/png;base64,'+info.image.icon_128+'" class="col-sm-2 va" />';
            }
            
            var name;
            if (info.image.ui_name !== '') {
                name = info.image.ui_name;
            } else {
                name = info.image.name;
            }
            html += '<div class="col-sm-7 va"><h4>'+name+'</h4></div>';

            var cls, text, stop_style;
            if (info.container !== null) {
                cls = "view-button btn-success";
                text = " View";
                stop_style = "";
            } else {
                cls = "start-button btn-primary";
                text = " Start";
                stop_style = 'style="visibility: hidden;"';
            }
            html += '<div class="col-sm-1 va">';
            html += '<button id="bnx_'+index+'" data-index="'+index+'" class="'+cls+' btn bnx"><i class="fa fa-spinner fa-spin" aria-hidden="true" style="display: none;"></i> <span>'+text+'</span></button>';
            html += '</div>';
            html += '<div class="col-sm-1 va">';
            html += '<button id="bny_'+index+'" data-index="'+index+'" class="stop-button btn btn-danger bny" '+stop_style+'><i class="fa fa-spinner fa-spin" aria-hidden="true" style="display: none"></i> Stop</button>';
            html += '</div>';
            html += '</div>';
            return html;
        };

        var reset_buttons_to_start = function (index) {
            // Used to revert the buttons to their "start" state when the
            // User clicks on "stop". 
            $("#bnx_"+index)
                .removeClass("view-button btn-success")
                .addClass("start-button btn-primary");
            $("#bnx_"+index+" > span").text(" Start");
            $("#bny_"+index).hide();
        };

        var render_applist = function () {
            // Renders the full application list and adds it to the DOM.
            var html = "";
            for (var i = 0; i < application_model.length; i++) {
                var info = application_model[i];
                html += render_applist_entry(i, info);
            }
            $("#applist").html(html);
        };
      
        var x_button_clicked = function () {
            // Triggered when the button X (left side) is clicked
            var button = this;
            var index = $(button).data("index");
            $(button).find(".fa-spinner").show();
            var app_info = application_model[index];

            if (app_info.container !== null) {
                // The container is already running, this is a View button
                window.location = utils.url_path_join(
                    base_url, 
                    "containers", 
                    app_info.container.url_id);
            } else {
                // The container is not running. This is a start button. 
                var mapping_id = application_model[index].mapping_id;
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

        var y_button_clicked = function () {
            // Triggered when the button Y (right side) is clicked
            var button = this;
            var index = $(button).data("index");
            $(button).find(".fa-spinner").show();
            var app_info = application_model[index];

            var url_id = app_info.container.url_id;
            appapi.stop_application(url_id, {
                success: function () {
                    $(button).find(".fa-spinner").hide();
                    reset_buttons_to_start(index);
                    app_info.container = null;
                },
                error: function (jqXHR, status, error) {
                    report_error(jqXHR, status, error);
                    $(button).find(".fa-spinner").hide();
                }
            });
        };
        
        var register_button_eventhandlers = function () {
            // Registers the event handlers on the buttons after addition
            // of the new entries to the list.
            $(".bnx").click(x_button_clicked);
            $(".bny").click(y_button_clicked);
        };
        
        var sync_local_model = function (app_data) {
            application_model = app_data;
        };
        
        $.when(appapi.available_applications_info())
            .done(sync_local_model)
            .done(render_applist)
            .done(register_button_eventhandlers);
        ;

    }
);
