define([
    "urlutils",
], function(urlutils) {
    "use strict";

    // Ember Helpers

    var helpers = {};

    helpers.IconSrcHelper = Ember.Helper.helper(function(params) {
        var icon_data = params[0].image.icon_128;
        return (
            icon_data ?
            "data:image/png;base64," + icon_data :
            urlutils.path_join(
                this.base_url, "static", "images", "generic_appicon_128.png"
            )
        );
    });

    helpers.AppNameHelper = Ember.Helper.helper(function(params) {
        return (
            params[0].image.ui_name ?
            params[0].image.ui_name :
            params[0].image.name
        );
    });

    // Application status helpers
    helpers.IsRunningHelper = Ember.Helper.helper(function(params) {
        return params[0] === 'running';
    });

    helpers.IsStoppedHelper = Ember.Helper.helper(function(params) {
        return params[0] === 'stopped';
    });

    helpers.IsStartingHelper = Ember.Helper.helper(function(params) {
        return params[0] === 'starting';
    });

    helpers.IsStoppingHelper = Ember.Helper.helper(function(params) {
        return params[0] === 'stopping';
    });


    helpers.EqualHelper = Ember.Helper.helper(function(params) {
        return params[0] === params[1];
    });

    helpers.NotNullHelper = Ember.Helper.helper(function(params) {
        return params[0] !== null;
    });

    // Logical helpers
    helpers.AndHelper = Ember.Helper.helper(function(params) {
        return params.reduce(function(a, b) {
            return a && b;
        });
    });

    helpers.OrHelper = Ember.Helper.helper(function(params) {
        return params.reduce(function(a, b) {
            return a || b;
        });
    });

    return helpers;
});
