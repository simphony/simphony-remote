// This module contains the setup for google analytics.
// MUST not be renamed to analytics. Some blockers rely on name 
// matching to prevent loading.
define([
], function () {
    "use strict";

    function init() {
        var module;
        
        if (window.apidata.analytics !== undefined) {
            window.ga('create', window.apidata.analytics.tracking_id, 'auto');
        } else {
            window.ga = function () {
            };
        }
        module = function () {
            window.ga.apply(this, arguments);
        };
        return module;
    } 

    return {
        init: init
    };
});
