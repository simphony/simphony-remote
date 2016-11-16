define([
    "jquery", 
    "urlutils",
    "handlebars",
    "underscore"
], function ($, urlutils, hb) {
    "use strict";
    var templates = {
       app_entries: hb.compile(
           '<li data-index="{{index}}">' +
           '  <span class="{{app_status}}-badge"></span>' +
           '  <a href="#" class="truncate">' +
           '    <img src="{{icon_src app_data}}" class="app-icon">' +
           '    <button class="stop-button" data-index="{{index}}"><i class="fa fa-times"></i></button>' +
           '    <span>{{image_name app_data}}</span>' +
           '  </a>' +
           '</li>')
    };

    var ApplicationListView = function(model) { 
        // (Constructor) Represents the application list. In charge of 
        // rendering in on the div with id #applist
        // 
        // Parameters
        // model : ApplicationListModel
        //     The data model.
        var self = this;
        self.model = model;

        $("#applist").html(
            '<li><a href="#"><i class="fa fa-spinner fa-spin"></i> <span>Loading</span></a></li>'
        );
    };

    ApplicationListView.prototype.entry_clicked = function(index) {
        // handler when entry has been clicked. Override in controller.
    };
    
    ApplicationListView.prototype.stop_button_clicked = function(index) {
        // handler when stop has been clicked. Override in controller.
    };
    
    ApplicationListView.prototype.render = function () {
        // Renders the full application list and adds it to the DOM.
        var self = this;
        var num_entries = this.model.app_data.length;
        var row;
        var applist = $("#applist");
        applist.empty();
        if (num_entries === 0) {
            row = $('<li><a href="#">No applications found</a></li>');
            applist.append(row);
        } else {
            for (var i = 0; i < num_entries; i++) {
                row = self._render_applist_entry(i);
                applist.append(row.hide().fadeIn(500));
            }
        }
        self.update_selected();
    };

    ApplicationListView.prototype.update_entry = function (index) {
        // Re-renders the entry for a given index, replacing the
        // current entry.
        var self = this;
        var row = this._render_applist_entry(index);
        $("#applist")
            .find("li[data-index='"+index+"']")
            .replaceWith(row);
        
        if (self.model.selected_index === index) {
            self.update_selected();
        }
    };

    ApplicationListView.prototype.update_selected = function() {
        // Updates the list against the current selected entry.
        var self = this;
        var applist = $("#applist");
        var selected_index = self.model.selected_index;
        applist.find("li").removeClass("active");
        if (selected_index !== null) {
            applist.find("li[data-index='"+selected_index+"']")
                .addClass("active");
        }
    };

    ApplicationListView.prototype._render_applist_entry = function (index) {
        // Returns a jquery HTML snippet for a single application entry
        // The returned entity has event handlers already installed.
        // index: 
        //     a progressive index for the entry.
        var self = this;
        var app_data = self.model.app_data[index];
        var app_status = self.model.status[index];

        var row = templates.app_entries({
            index: index,
            app_data: app_data,
            app_status: app_status.toLowerCase()
        });
        
        var jq_row = $(row);
        jq_row.click(function() {
            self.entry_clicked($(this).attr("data-index"));
        });
        jq_row.find(".app-icon").hover(function() {
            var app_data = self.model.app_data[index];
            if (app_data.container !== null) {
                jq_row.find(".stop-button").show();
            }
        }, null);
        
        jq_row.find(".stop-button")
            .hide()
            .click(function(event) {
                event.stopPropagation();
                self.stop_button_clicked($(this).attr("data-index"));
            })
            .hover(null, function() {
                jq_row.find(".stop-button").hide();
            });
        return jq_row;
    };
   
    return {
        ApplicationListView : ApplicationListView
    };
});
