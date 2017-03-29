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
