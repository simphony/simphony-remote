define([
    "jquery", 
    "urlutils",
    "handlebars"
], function ($, urlutils, hb) {
    "use strict";

    var templates = {
       app_entries: hb.compile(
           '<li class="active" data-index="{{index}}">' +
           '<a href="#">' +
           '  <img src="{{icon}}" class="app-icon">' +
           '    <span>{{image_name}}</span></a>' +
           '</li>')
    };

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
        this.stop_button_clicked = function(index) {}; // jshint ignore:line
        this.start_button_clicked = function(index) {}; // jshint ignore:line
        this.view_button_clicked = function(index) {}; // jshint ignore:line

        this._x_button_clicked = function () {
            // Triggered when the button X (left side) is clicked
            var button = $(this);
            var index = button.data("index");

            var icon_elem = button.find(".x-icon");
            var icons = ['fa-start', 'fa-eye'];
            var icon_type;

            for (var i = 0; i < icons.length; ++i) {
                if (icon_elem.hasClass(icons[i])) {
                    icon_type = icons[i];
                }
            }
            
            var update_entry = function () { self.update_entry(index); };
            icon_elem.removeClass(icon_type).addClass("fa-spinner fa-spin");
            button.prop("disabled", true);
            
            var app_info = self.model.app_data[index];
            if (app_info.container !== null) {
                self.view_button_clicked(index).always(update_entry);
            } else {
                self.start_button_clicked(index).always(update_entry);
            }
        };
        
        this._y_button_clicked = function () {
            var button = $(this);
            var index = button.data("index");
            var icon_elem = button.find(".y-icon");
            
            icon_elem.removeClass("fa-stop").addClass("fa-spinner fa-spin");
            button.prop("disabled", true);

            var update_entry = function () { self.update_entry(index); };
            self.stop_button_clicked(index).always(update_entry);
        };
        
        $("#applist").html(
            '<li class="active"><a href="#"><i class="fa fa-spinner fa-spin"></i> <span>Loading</span></a></li>'
        );
    };

    ApplicationListView.prototype.render = function () {
        // Renders the full application list and adds it to the DOM.
        var num_entries = this.model.app_data.length;
        var row;
        var applist = $("#applist");
        applist.empty();
        if (num_entries === 0) {
            row = $('<li class="active"><a href="#">No applications found</li>');
            applist.append(row);
        } else {
            for (var i = 0; i < num_entries; i++) {
                row = this.render_applist_entry(i);
                applist.append(row.hide().fadeIn(500));
            }
        }
    };
    
    ApplicationListView.prototype.render_applist_entry = function (index) {
        // Returns a HTML snippet for a single application entry
        // index: 
        //     a progressive index for the entry.
        
        var app_data = this.model.app_data[index];

        var icon = app_data.image.icon_128 ?
            "data:image/png;base64,"+app_data.image.icon_128 :
            urlutils.path_join(this.base_url,
                "static", "images", "generic_appicon_128.png");

        var image_name = app_data.image.ui_name ? app_data.image.ui_name : app_data.image.name;

        var row = templates.app_entries({
            icon: icon,
            image_name: image_name,
            index: index
        });
        
        var jq_row = $(row);
        return jq_row;
    };
    
    ApplicationListView.prototype.update_entry = function (index) {
        // Re-renders the entry for a given index, replacing the
        // current entry.
        var row = this.render_applist_entry(index);
        $("#applist")
            .find(".row[data-index='"+index+"']")
            .replaceWith(row);
    };

    return {
        ApplicationListView : ApplicationListView
    };
});
