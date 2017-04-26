// Based on IPython's base.js.utils
// Original Copyright (c) IPython Development Team.
// Distributed under the terms of the Modified BSD License.

// Modifications Copyright (c) Juptyer Development Team.
// Distributed under the terms of the Modified BSD License.

define([
    'jquery'
], function ($) {
    "use strict";

    var all = function (promises) {
        // A form of jQuery.when that handles an array of promises
        // and equalises the behavior regardless if there's one or more than
        // one elements.
        if (!Array.isArray(promises)) {
            throw new Error("$.all() must be passed an array of promises");
        }
        return $.when.apply($, promises).then(function () {
            // if single argument was expanded into multiple arguments,
            // then put it back into an array for consistency
            if (promises.length === 1 && arguments.length > 1) {
                // put arguments into an array
                return [Array.prototype.slice.call(arguments, 0)];
            } else {
                return Array.prototype.slice.call(arguments, 0);
            }
        });
    };

    var update = function (d1, d2) {
        // Transfers the keys from d2 to d1. Returns d1
        $.map(d2, function (i, key) {
            d1[key] = d2[key];
        });
        return d1;
    };

    var max_iframe_size = function () {
        // Returns the current iframe viewport size
        var body = $("body");
        var height = body.height() - $(".header").outerHeight();
        var width = body.width() - $(".main-sidebar").outerWidth();
        return [width, height];
    };

    var Status = {
        RUNNING: "RUNNING",
        STARTING: "STARTING",
        STOPPING: "STOPPING",
        STOPPED: "STOPPED"
    };

    // Temporary: will be registered in Vue globally
    var filters = {
        icon_src: function(icon_data) {
            return (
                icon_data ?
                'data:image/png;base64,' + icon_data :
                urlutils.path_join(
                    window.apidata.base_url, 'static', 'images', 'generic_appicon_128.png'
                )
            );
        },
        app_name: function(image) {
            return image.ui_name? image.ui_name: image.name;
        },
        is_starting: function(application) {
            return application.status === Status.STARTING;
        }
    }

    return {
        all : all,
        update : update,
        max_iframe_size: max_iframe_size,
        filters: filters,
        Status: Status
    };

});
