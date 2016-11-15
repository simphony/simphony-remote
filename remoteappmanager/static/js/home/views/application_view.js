define([
    "jquery", 
    "urlutils",
    "handlebars",
    "utils"
], function ($, urlutils, hb, utils) {
    "use strict";
    var templates = {
       app_start_panel: hb.compile(
           '<div class="configuration">' +
           '  <div class="box box-primary">' +
           '    <div class="box-header with-border">' +
           '      <h3 class="box-title">{{image_name app_data}}</h3>' +
           '      <div class="box-tools pull-right"></div>' +
           '    </div>' +
           '    <div class="box-body"></div>' +
           '    <div class="box-footer">' +
           '      <a href="#" data-index={{index}} class="btn btn-primary pull-right start-button">Start</a>' +
           '    </div>' +
           '  </div>' +
           '</div>'
       )
    };

    var ApplicationView = function(model) {
        // (Constructor) Represents the application list. In charge of 
        // rendering in on the div with id #applist
        // 
        // Parameters
        // model : ApplicationListModel
        //     The data model.
        var self = this;
        self.model = model;
        self.base_url = window.apidata.base_url;
    };

    ApplicationView.prototype.start_button_clicked = function(index) {}; // jshint ignore:line

    ApplicationView.prototype.render = function (delayed) {
        // Renders the ApplicationView.
        // delayed:
        //    When true, if the application is running it will redirect to
        //    the waiting spinner, rather than the application itself.
        //    Temporary measure. Will go away.
        var self = this;
        var index = self.model.selected_index;
        
        if (index === null) {
            // render nothing.
            return;
        }
        
        var app_data = self.model.app_data[index];
        
        if (app_data.container === null) {
            self._render_form(index);
        } else {
            self._render_app(index, delayed);
        }
    };
    
    ApplicationView.prototype._render_form = function(index) {
        var self = this;
        var app_data = self.model.app_data[index];
        var form = $("<form class='configuration'>");

        var configurables = self.model.configurables[index];
        var properties = Object.getOwnPropertyNames(configurables);
        
        if (properties.length === 0) {
            form.html("No configurable options for this image");
        } else {
            properties.forEach(
                function(val) {  // jshint ignore:line
                    var widget = configurables[val].view(index);
                    form.append(widget);
                }
            );
        }

        var base = $(templates.app_start_panel({
            app_data: app_data,
            index: index
        }));

        base.find(".box-body").html(form);
        base.find(".start-button").click(function() {
            self.start_button_clicked($(this).attr("data-index"));
        });

        $(".content").html(base.hide().fadeIn(200));
    };
    
    ApplicationView.prototype._render_app = function(index, delayed) {
        var self = this;
        var app_data = self.model.app_data[index];
        var location = urlutils.path_join(self.base_url, 
            "containers", 
            app_data.container.url_id
        );
        
        if (!delayed) {
            location = location+"/";
        }    
        
        var iframe_size = utils.max_iframe_size();
        var iframe = $('<iframe class="application" frameBorder="0" ' +
            'src="' + location + '" ' +
            'style="min-width: '+iframe_size[0]+'px; min-height: '+iframe_size[1]+'px;"></iframe>');
        $(".content").html(iframe.hide().fadeIn(200));
    };

    return {
        ApplicationView : ApplicationView
    };
});
