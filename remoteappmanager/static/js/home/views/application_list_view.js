define([
    "jquery", 
    "urlutils",
    "handlebars",
], function ($, urlutils, hb) {
    "use strict";
    
    hb.registerHelper('icon_src', function(app_data) {
        var icon_data = app_data.image.icon_128;
        return (icon_data ? "data:image/png;base64,"+icon_data :
                urlutils.path_join(this.base_url, "static", "images", "generic_appicon_128.png"))
        }
    );
    hb.registerHelper('image_name', function(app_data) {
        return (app_data.image.ui_name ? app_data.image.ui_name : app_data.image.name);
    });
    
    var templates = {
       app_entries: hb.compile(
           '<li data-index="{{index}}">' +
           '<a href="#">' +
           '  <img src="{{icon_src app_data}}" class="app-icon">' +
           '    <span>{{image_name app_data}}</span></a>' +
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

        $("#applist").html(
            '<li><a href="#"><i class="fa fa-spinner fa-spin"></i> <span>Loading</span></a></li>'
        );
    };

    ApplicationListView.prototype.entry_clicked = function(index) {
        // handler when entry has been clicked. Override in controller.
    };
    
    ApplicationListView.prototype.render = function () {
        // Renders the full application list and adds it to the DOM.
        var num_entries = this.model.app_data.length;
        var row;
        var applist = $("#applist");
        applist.empty();
        if (num_entries === 0) {
            row = $('<li><a href="#">No applications found</a></li>');
            applist.append(row);
        } else {
            for (var i = 0; i < num_entries; i++) {
                row = this._render_applist_entry(i);
                applist.append(row.hide().fadeIn(500));
            }
        }
    };

    ApplicationListView.prototype.update_entry = function (index) {
        // Re-renders the entry for a given index, replacing the
        // current entry.
        var row = this._render_applist_entry(index);
        $("#applist")
            .find(".li[data-index='"+index+"']")
            .replaceWith(row);
    };


    ApplicationListView.prototype._render_applist_entry = function (index) {
        // Returns a HTML snippet for a single application entry
        // index: 
        //     a progressive index for the entry.
        var self = this;
        var app_data = this.model.app_data[index];

        var row = templates.app_entries({
            index: index,
            app_data: app_data
        });
        
        var jq_row = $(row);
        jq_row.click(function() {
            self.entry_clicked($(this).attr("data-index"));
        });
        return jq_row;
    };
   
    return {
        ApplicationListView : ApplicationListView
    };
});
