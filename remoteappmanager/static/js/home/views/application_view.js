define([
    "jquery", 
    "urlutils",
    "handlebars",
    "utils",
    "underscore",
    "home/models"
], function ($, urlutils, hb, utils, _, models) {
    "use strict";
    var templates = {
       app_start_panel: hb.compile(
           '<div class="configuration">' +
           '  <div class="box box-primary">' +
           '    <div class="box-header with-border">' +
           '      <h3 class="box-title">{{image_name app_data}}</h3>' +
           '      <div class="box-tools pull-right"></div>' +
           '    </div>' +
           '    <div class="box-body">' +
           '      <h4>Policy</h4>' +
           '      <ul class="policy">' +
           '      </ul>' +
           '      <h4>Configuration</h4>' +
           '      <form class="configuration"><fieldset {{#if disabled}}disabled{{/if}}></fieldset></form>' +
           '    </div>' +
           '    <div class="box-footer">' +
           '      <button data-index={{index}} class="btn btn-primary pull-right start-button" {{#if disabled}}disabled{{/if}}>Start</button>' +
           '    </div>' +
           '  </div>' +
           '</div>'
       )
    };

    var ApplicationView = function(model) {
        // (Constructor) Represents the main view where the application will be
        // 
        // Parameters
        // model : ApplicationListModel
        //     The data model.
        var self = this;
        self.model = model;
        self.visualised_index = null;
        self.base_url = window.apidata.base_url;
    };

    ApplicationView.prototype.start_button_clicked = function(index) {}; // jshint ignore:line

    ApplicationView.prototype.render = function (delayed, fade_in) {
        // Renders the ApplicationView.
        // delayed:
        //    When true, if the application is running it will redirect to
        //    the waiting spinner, rather than the application itself.
        //    Temporary measure. Will go away.
        var self = this;
        if (self.visualised_index === self.model.selected_index &&
            self.visualised_status === self.model.status[self.model.selected_index]) {
            return;
        }
        var html = self._render_for_model_state(delayed);
        self.visualised_index = self.model.selected_index;
        self.visualised_status = self.model.status[self.visualised_index];
        if (fade_in) {
            $(".content").html(html.hide().fadeIn(fade_in));
        } else {
            $(".content").html(html);
        }
    };
   
    ApplicationView.prototype._render_for_model_state = function(delayed) {
        // Decides what to render according to the current model state
        var self = this;
        var index = self.model.selected_index;

        if (index === null) {
            // render nothing.
            return $("<div>");
        }

        var app_status = self.model.status[index];
        var html;

        if (app_status === models.Status.STARTING || app_status === models.Status.STOPPED) {
            html = self._render_form(index);
        } else {
            html = self._render_app(index, delayed);
        }
        return html;
    };
    
    ApplicationView.prototype._render_form = function(index) {
        // Renders the configuration form
        var self = this;
        var app_data = self.model.app_data[index];
        var app_status = self.model.status[index];

        var configurables = self.model.configurables[index];
        var properties = Object.getOwnPropertyNames(configurables);

        var disabled = (app_status === models.Status.STARTING);
        
        var base = $(templates.app_start_panel({
            app_data: app_data,
            index: index,
            disabled: disabled
        }));
        
        base.find(".start-button").click(function() {
            self.start_button_clicked($(this).attr("data-index"));
        });


        var policy = app_data.image.policy;
        var policy_ul = base.find(".policy");
        
        if (policy.allow_home) {
            policy_ul.append($("<li>Workspace accessible</li>"));
        } else {
            policy_ul.append($("<li>Workspace not accessible</li>"));
        }
        
        if (policy.volume_source && policy.volume_target && policy.volume_mode) {
            policy_ul.append($(
                "<li>Volume mounted: " + policy.volume_source +
                " &#x2192; " + policy.volume_target +
                " (" + policy.volume_mode + ")</li>"));
        } else {
            policy_ul.append($("<li>No volumes mounted</li>"));
        }
                
        var fieldset = base.find("fieldset");
        
        if (properties.length === 0) {
            fieldset.html("No configurable options for this image");
        } else {
            properties.forEach(
                function(val) {  // jshint ignore:line
                    var widget = configurables[val].view(index);
                    fieldset.append(widget);
                }
            );
        }

        return base;
    };
    
    ApplicationView.prototype._render_app = function(index, delayed) {
        // Renders the iframe with the application.
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
        var iframe = $('<iframe id="application" frameBorder="0" ' +
            'src="' + location + '" ' +
            'style="min-width: '+iframe_size[0]+'px; min-height: '+iframe_size[1]+'px;"></iframe>');
        return iframe;
    };

    return {
        ApplicationView : ApplicationView
    };
});
