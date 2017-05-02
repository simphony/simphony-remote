// This module contains the setup for google analytics.
// MUST not be renamed to analytics. Some blockers rely on name
// matching to prevent loading.
define([
    "components/vue/dist/vue.min"
], function (Vue) {
    "use strict";

    function init() {
        if (window.apidata.analytics !== undefined) {
            window.ga('create', window.apidata.analytics.tracking_id, 'auto');
        } else {
            window.ga = function() {};
        }

        return function() {
            window.ga.apply(this, arguments);
        };
    }

    var GaObserver = function() {
        this.ga = init();
    };

    GaObserver.prototype.trigger_application_starting = function(name) {
        this.ga("send", "event", {
            eventCategory: "Application",
            eventAction: "start",
            eventLabel: name
        });
    };

    return {
        init: init, // For testing purpose
        GaObserver: GaObserver
    };
});
