define(["jquery", "utils", "initialization"], function ($, utils, initialization) {
    "use strict";
    
    var ApplicationListView = function(model) { 
        this.model = model;
        var self = this;
        
        self.base_url = window.apidata.base_url;

        this.stop_button_clicked = function() {};
        this.start_button_clicked = function() {};
        this.view_button_clicked = function() {};
        
        this._x_button_clicked = function () {
            // Triggered when the button X (left side) is clicked
            var button = this;
            var index = $(button).data("index");
            $(button).find(".fa-spinner").show();

            var app_info = self.model.data[index];
            
            var hide_spinner = function () {
                $(button).find(".fa-spinner").hide();
            };
            
            if (app_info.container !== null) {
                self.view_button_clicked(index).done(hide_spinner);
            } else {
                self.start_button_clicked(index).done(hide_spinner);
            }
        };
        
        this._y_button_clicked = function () {
            var button = this;
            var index = $(button).data("index");
            $(button).find(".fa-spinner").show();
            self.stop_button_clicked(index).done(function () {
                    $(button).find(".fa-spinner").hide();
            });
        };
    };

    ApplicationListView.prototype.render = function () {
        // Renders the full application list and adds it to the DOM.
        var html = "";
        for (var i = 0; i < this.model.data.length; i++) {
            var info = this.model.data[i];
            html += this.render_applist_entry(i, info);
        }
        $("#applist").html(html);
        this.register_button_eventhandlers();
    };
    
    ApplicationListView.prototype.render_applist_entry = function (index, info) {
        // Returns a HTML snippet for a single application entry
        // index: 
        //     a progressive index for the entry.
        // info:
        //     A dictionary containing the retrieved data about the application
        //     and (possibly) the container.
        var html = '<div class="row">';

        if (info.image.icon_128) {
            html += '<img src="data:image/png;base64,'+info.image.icon_128+'" class="col-sm-2 va" />';
        } else {
            html += '<img src="' + utils.url_path_join(
                    this.base_url, "static", "images", "generic_appicon_128.png") +
                '" class="col-sm-2 va" />';
        }

        var name;
        if (info.image.ui_name) {
            name = info.image.ui_name;
        } else {
            name = info.image.name;
        }
        html += '<div class="col-sm-7 va"><h4>'+name+'</h4>';

        var policy = info.image.policy;
        var mount_html = '';

        if (policy.allow_home) {
            mount_html += "<li>Workspace</li>";
        }
        if (policy.volume_source && policy.volume_target && policy.volume_mode) {
            mount_html += "<li>"+ policy.volume_source +
                " &#x2192; " +
                policy.volume_target +
                " " +
                "(" + policy.volume_mode + ")</li>";
        }
        if (mount_html !== '') {
            html += "<ul>" + mount_html + "</ul>";
        }

        html += '</div>';

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
    
    ApplicationListView.prototype.reset_buttons_to_start = function (index) {
        // Used to revert the buttons to their "start" state when the
        // User clicks on "stop". 
        $("#bnx_"+index)
            .removeClass("view-button btn-success")
            .addClass("start-button btn-primary");
        $("#bnx_"+index+" > span").text(" Start");
        $("#bny_"+index).hide();
    };
    
    ApplicationListView.prototype.register_button_eventhandlers = function () {
        // Registers the event handlers on the buttons after addition
        // of the new entries to the list.
        $(".bnx").click(this._x_button_clicked);
        $(".bny").click(this._y_button_clicked);
    };

    return {
        ApplicationListView : ApplicationListView
    };
    
    
});
