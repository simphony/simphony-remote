define([
    "jquery",
    "handlebars",
    "utils"
], function($, hb, utils) {
    "use strict";

    var view_template = hb.compile(
        '<div class="form-group">' +
        '<label for="resolution-model-{{index}}">Resolution</label>' +
        '<select class="form-control" id="resolution-model-{{ index }}">' +
        '{{#each options}}' +
           '<option value="{{this}}">{{this}}</option>' +
        '{{/each}}' +
        '</div>'
    );

    var ResolutionModel = function () {
        // Model for the resolution configurable.
        var self = this;
        this.resolution = "Window";
        this.resolution_options = ["Window", "1920x1080", "1280x1024", "1280x800", "1024x768"];
       
        self.view = function (index) {
            // Creates the View to add to the application entry.
            var widget = $(view_template({
                options: self.resolution_options,
                index: index
            }));
            
            widget.find("select").change(function() {
                if (this.selectedIndex) {
                    self.resolution = this.options[this.selectedIndex].value;
                }
            });
            
            return widget;
        };
    };
    
    ResolutionModel.prototype.tag = "resolution";
   
    ResolutionModel.prototype.as_config_dict = function() {
        // Returns the configuration dict to hand over to the API request.
        // e.g. 
        // {
        //    "resolution" : "1024x768"
        // }
        // The returned dictionary must be added to the configurable
        // parameter under the key given by the tag member. 
        var resolution = this.resolution;
        
        if (resolution === 'Window') {
            var max_size = utils.max_iframe_size();
            resolution = max_size[0]+"x"+max_size[1];
        }
        
        return {
            "resolution": resolution
        };
    };
   
    // Define all your configurables here.
    var configurables = {
        ResolutionModel: ResolutionModel
    };
    
    var from_tag = function (tag) {
        // Given a tag, lookup the appropriate configurable and
        // return it. If the tag matches no configurable, returns null
        for (var conf in configurables) {
            if (configurables[conf].prototype.tag === tag) {
                return configurables[conf];
            }
        }
        return null; 
    };

    var ns = {
        from_tag: from_tag
    };

    return $.extend(ns, configurables);
    
});
