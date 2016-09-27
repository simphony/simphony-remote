define(["jquery", "utils"], function ($, utils) {
    "use strict";

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

            var icon_elem = $(button).find(".x-icon");
            var icons = ['fa-start', 'fa-eye'];
            var icon_type;

            for (var i = 0; i < icons.length; ++i) {
                if (icon_elem.hasClass(icons[i])) {
                    icon_type = icons[i];
                }
            }
            
            var update_entry = function () { self.update_entry(index); };
            icon_elem.removeClass(icon_type).addClass("fa-spinner fa-spin");
            
            var app_info = self.model.app_data[index];
            if (app_info.container !== null) {
                self.view_button_clicked(index).always(update_entry);
            } else {
                self.start_button_clicked(index).always(update_entry);
            }
        };
        
        this._y_button_clicked = function () {
            var button = this;
            var index = $(button).data("index");
            var icon_elem = $(button).find(".y-icon");
            
            icon_elem.removeClass("fa-stop").addClass("fa-spinner fa-spin");

            var update_entry = function () { self.update_entry(index); };
            self.stop_button_clicked(index).always(update_entry);
        };
        
        $("#applist").html(
            '<div class="col-sm-12 text-center">' +
            '<i class="fa fa-4x fa-spinner fa-spin" aria-hidden="true"></i>' +
            '</div>');
    };

    ApplicationListView.prototype.render = function () {
        // Renders the full application list and adds it to the DOM.
        var num_entries = this.model.app_data.length;
        var row;
        var applist = $("#applist");
        applist.empty();
        if (num_entries === 0) {
            row = $('<div class="col-sm-12 text-center va"><h4>No applications found</h4></div>');
            applist.append(row);
        } else {
            for (var i = 0; i < num_entries; i++) {
                row = this.render_applist_entry(i);
                applist.append(row);
            }
        }
    };
    
    ApplicationListView.prototype.render_applist_entry = function (index) {
        // Returns a HTML snippet for a single application entry
        // index: 
        //     a progressive index for the entry.
        
        var app_data = this.model.app_data[index];
        var configurables = this.model.configurables[index];
        
        var html_template = '' +
            '<div class="row" data-index="{index}">' +
            '  <img src="{icon}" class="col-sm-2 va" />' +
            '  <div class="col-sm-7 va">' +
            '    <h4>{image_name}</h4>' +
            '    <div class="policy">{policy_html}</div>' +
            '    <div class="configurables"></div>' +
            '  </div>' +
            '  <div class="col-sm-1 va">' +
            '    <button id="bnx_{index}" data-index="{index}" class="{button_x_class} bnx btn"><span> <i class="fa {button_x_icon} x-icon"></i> {button_x_text}</span></button>' +
            '  </div>' +
            '  <div class="col-sm-1 va" style="padding-left: 30px">' + 
            '    <button id="bny_{index}" data-index="{index}" class="stop-button btn-danger bny btn" style="{button_y_style}"><span><i class="fa fa-stop y-icon" aria-hidden="true"></i> Stop</span></button>' +
            '  </div>' +
            '</div>';

        var icon = app_data.image.icon_128 ?
            "data:image/png;base64,"+app_data.image.icon_128 :
            utils.url_path_join(this.base_url,
                "static", "images", "generic_appicon_128.png");

        var image_name = app_data.image.ui_name ? app_data.image.ui_name : app_data.image.name;
        var policy_html = this._policy_html(app_data.image.policy);
        var cls, text, stop_style, x_icon;
        if (app_data.container !== null) {
            cls = "view-button btn-success";
            text = " View";
            x_icon = "fa-eye";
            stop_style = "";
        } else {
            cls = "start-button btn-primary";
            x_icon = "fa-play";
            text = " Start";
            stop_style = 'visibility: hidden;';
        }
        
        var row = $(html_template
            .replace(/\{icon\}/g, icon)
            .replace(/\{image_name\}/g, image_name)
            .replace(/\{policy\}/g, policy_html)
            .replace(/\{index\}/g, index)
            .replace(/\{button_x_class\}/g, cls)
            .replace(/\{button_x_icon\}/g, x_icon)
            .replace(/\{button_x_text\}/g, text)
            .replace(/\{button_y_style\}/g, stop_style)
            .replace(/\{policy_html\}/g, policy_html));
         
        row.find(".bnx").click(this._x_button_clicked);
        row.find(".bny").click(this._y_button_clicked);
        
        if (app_data.container === null) {
            var ul = $("<ul>");
            Object.getOwnPropertyNames(configurables).forEach(
                function(val, idx, array) {
                    var widget = configurables[val].view();
                    ul.append($("<li>").append(widget));
                }
            );
            row.find(".configurables").append(ul);
        }
        
        return row;
    };
    
    ApplicationListView.prototype.update_entry = function (index) {
        // Re-renders the entry for a given index, replacing the
        // current entry.
        console.log("updating entry");
        var row = this.render_applist_entry(index);
        $("#applist")
            .find(".row[data-index='"+index+"']")
            .replaceWith(row);
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

    return {
        ApplicationListView : ApplicationListView
    };
    
    
});
