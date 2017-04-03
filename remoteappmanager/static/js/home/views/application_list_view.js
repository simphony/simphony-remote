define([
    "jquery",
    "urlutils",
    "handlebars",
    "underscore"
], function ($, urlutils, hb) {
    "use strict";

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
