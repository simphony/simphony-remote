define(["jquery"], function($) {
    "use strict";
    
    function viewport_resolution() {
        // Returns the current viewport resolution as a "WxH" string
        var e = window, a = 'inner';
        if ( !( 'innerWidth' in window ) ) {
            a = 'client';
            e = document.documentElement || document.body;
        }
        return e[ a+'Width' ]+"x"+e[ a+'Height' ];
    }

    var ResolutionModel = function () {
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
        var resolution = this.resolution;
        
        if (resolution === 'Window') {
            resolution = viewport_resolution();
        }
        
        return {
            "resolution": resolution
        };
    };
    
    var configurables = {
        ResolutionModel: ResolutionModel
    };
    
    var from_tag = function (tag) {
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
