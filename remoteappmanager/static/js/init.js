define([
    "handlebars",
    "urlutils"
], function(hb, urlutils) {
    "use strict";
   
    return {
        handlebars : function() {
            hb.registerHelper('icon_src', function(app_data) {
                    var icon_data = app_data.image.icon_128;
                    return (icon_data ? "data:image/png;base64,"+icon_data :
                        urlutils.path_join(this.base_url, "static", "images", "generic_appicon_128.png"));
                }
            );
            hb.registerHelper('image_name', function(app_data) {
                return (app_data.image.ui_name ? app_data.image.ui_name : app_data.image.name);
            });

        }
    };
});
