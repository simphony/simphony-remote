define(["jquery", "utils"], function ($, utils) {
    "use strict";

    function viewport_resolution() {
        var e = window, a = 'inner';
        if ( !( 'innerWidth' in window ) ) {
            a = 'client';
            e = document.documentElement || document.body;
        }
        return e[ a+'Width' ]+"x"+e[ a+'Height' ];
    }
    
    var ApplicationListView = function(model) { 
        // (Constructor) Represents the application list. In charge of 
        // rendering in on the div with id #applist
        // 
        // Parameters
        // model : ApplicationListModel
        //     The data model.
        this.model = model;
        var self = this;
        
        self.base_url = window.apidata.base_url;

        // Handlers for button clicking.
        // replace them to override default behavior (doing nothing).
        // Can return a value or a promise.
        this.stop_button_clicked = function(index) {};
        this.start_button_clicked = function(index) {};
        this.view_button_clicked = function(index) {};
        
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
        
        $("#applist").html(
            '<div class="col-sm-12 text-center">' +
            '<i class="fa fa-4x fa-spinner fa-spin" aria-hidden="true"></i>' +
            '</div>');
    };

    ApplicationListView.prototype.render = function () {
        // Renders the full application list and adds it to the DOM.
        var num_entries = this.model.data.length;
        var row;
        var applist = $("#applist");
        applist.empty();
        if (num_entries === 0) {
            row = $('<div class="col-sm-12 text-center va"><h4>No applications found</h4></div>');
            applist.append(row);
        } else {
            for (var i = 0; i < num_entries; i++) {
                var info = this.model.data[i];
                row = this.render_applist_entry(i, info);
                applist.append(row);
            }
        }
    };
    
    ApplicationListView.prototype.render_applist_entry = function (index, info) {
        // Returns a HTML snippet for a single application entry
        // index: 
        //     a progressive index for the entry.
        // info:
        //     A dictionary containing the retrieved data about the application
        //     and (possibly) the container.
        var html_template = '' +
            '<div class="row">' +
            '  <img src="{icon}" class="col-sm-2 va" />' +
            '  <div class="col-sm-7 va">' +
            '    <h4>{image_name}</h4>' +
            '    <div class="policy">{policy_html}</div>' +
            '    <div class="configurables"></div>' +
            '  </div>' +
            '  <div class="col-sm-1 va">' +
            '    <button id="bnx_{index}" data-index="{index}" class="{button_x_class} bnx btn"><i class="fa fa-spinner fa-spin" aria-hidden="true" style="display: none;"></i> <span> {button_x_text}</span></button>' +
            '  </div>' +
            '  <div class="col-sm-1 va">' + 
            '    <button id="bny_{index}" data-index="{index}" class="stop-button btn-danger bny btn" style="{button_y_style}"><i class="fa fa-spinner fa-spin" aria-hidden="true" style="display: none;"></i> <span> Stop</span></button>' +
            '  </div>' +
            '</div>';

        var icon = info.image.icon_128 ?
            "data:image/png;base64,"+info.image.icon_128 :
            utils.url_path_join(this.base_url,
                "static", "images", "generic_appicon_128.png");

        var image_name = info.image.ui_name ? info.image.ui_name : info.image.name;
        var policy_html = this._policy_html(info.image.policy);
        var cls, text, stop_style;
        if (info.container !== null) {
            cls = "view-button btn-success";
            text = " View";
            stop_style = "";
        } else {
            cls = "start-button btn-primary";
            text = " Start";
            stop_style = 'visibility: hidden;';
        }
        
        var row = $(html_template
            .replace(/\{icon\}/g, icon)
            .replace(/\{image_name\}/g, image_name)
            .replace(/\{policy\}/g, policy_html)
            .replace(/\{index\}/g, index)
            .replace(/\{button_x_class\}/g, cls)
            .replace(/\{button_x_text\}/g, text)
            .replace(/\{button_y_style\}/g, stop_style)
            .replace(/\{policy_html\}/g, policy_html));
         
        row.find(".bnx").click(this._x_button_clicked);
        row.find(".bny").click(this._y_button_clicked);
        var configurables_widget = this._configurables(info.image.configurables_data);
        if (configurables_widget && info.container === null) {
            row.find(".configurables").append(
                $("<ul>").append(configurables_widget));
        }
        
        return row;
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
    

    ApplicationListView.prototype._policy_html = function(policy) {
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
            mount_html = "<ul>" + mount_html + "</ul>";
        }
        return mount_html;
    };

    ApplicationListView.prototype._configurables = function(configurables_model) {  
        var widget = null;
        if (configurables_model.hasOwnProperty("resolution")) {
            var current_res = viewport_resolution();
            configurables_model.resolution = current_res;
            var std_opts = "";
            var std_res = ["1920x1080", "1280x1024", "1280x800", "1024x768"];
            for (var i = 0; i < std_res.length; ++i) {
                std_opts += "<option value='"+std_res[i]+"'>"+std_res[i]+"</option>";
            }
            widget = $(
                "<li>Resolution: " +
                "<select>" +
                "   <option value='{current_res}' selected='selected'>Window</option>" +
                std_opts +
                "</select>" +
                "</li>".replace(/\{current_res\}/g, current_res)
            );
            widget.find("select").change(function() { 
                if (this.selectedIndex) {
                    configurables_model.resolution = this.options[this.selectedIndex].value;
                }
            });
        }
        return widget;
    };
    
    
    
    return {
        ApplicationListView : ApplicationListView
    };
    
    
});
