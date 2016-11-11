define([
    "require"
], function (require) {
    "use strict";
    
    function init() {
        var module;
        
        if (window.apidata.analytics !== undefined) {
            window.GoogleAnalyticsObject = "ga";
            window.ga = function () {
                (window.ga.q = window.ga.q || []).push(arguments);
            };
            window.ga.l = 1 * new Date();
            module = function () {
                window.ga.apply(this, arguments);
            };
            require(["//www.google-analytics.com/analytics.js"]);
            window.ga('create', window.apidata.analytics.tracking_id, 'auto');
        } else {
            window.ga = function () {
            };
            module = function () {
                window.ga.apply(this, arguments);
            };
        }
        return module;
    } 

    return {
        init: init
    };
});
