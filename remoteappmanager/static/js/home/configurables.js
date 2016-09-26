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
        this.resolution = "Window";
        this.resolution_options = ["Window", "1024x768", "1920x1080"];
    };
    
    ResolutionModel.tag = "resolution";
   
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
            if (configurables[conf].tag === tag) {
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
