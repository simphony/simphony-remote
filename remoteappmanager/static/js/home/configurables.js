define(["jquery"], function($) {
    "use strict";

    var ResolutionModel = function () {
        // Model for the resolution configurable.
        var self = this;
        this.resolution = "Window";
        this.resolution_options = ["Window", "1920x1080", "1280x1024", "1280x800", "1024x768"];
       
        self.view = function () {
            // Creates the View to add to the application entry.
            var opts = "";
            for (var i = 0; i < self.resolution_options.length; ++i) {
                var opt = self.resolution_options[i];
                opts += "<option value='" + opt + "'>" + opt + "</option>";
            }
            var widget = $("<p>" +
                "Resolution: " +
                "<select>" +
                opts +
                "</select></p>"
            );
            
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
            resolution = this._viewport_resolution();
        }
        
        return {
            "resolution": resolution
        };
    };
   
    ResolutionModel.prototype._viewport_resolution = function () {
        // Returns the current viewport resolution as a "WxH" string
        var e = window, a = 'inner';
        if ( !( 'innerWidth' in window ) ) {
            a = 'client';
            e = document.documentElement || document.body;
        }
        return e[ a+'Width' ]+"x"+e[ a+'Height' ];
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
