define([
    "urlutils",
], function(urlutils) {
    "use strict";

    // Ember Helpers

    var helpers = {};

    helpers.IconSrcHelper = Ember.Helper.helper(function([app_data]) {
        var icon_data = app_data.image.icon_128;
        return (
            icon_data ?
            "data:image/png;base64," + icon_data :
            urlutils.path_join(
                this.base_url, "static", "images", "generic_appicon_128.png"
            )
        );
    });

    helpers.AppNameHelper = Ember.Helper.helper(function([app_data]) {
        return (
            app_data.image.ui_name ?
            app_data.image.ui_name :
            app_data.image.name
        );
    });

    // Application status helpers
    helpers.IsRunningHelper = Ember.Helper.helper(function([status]) {
        return status === 'running';
    });

    helpers.IsStoppedHelper = Ember.Helper.helper(function([status]) {
        return status === 'stopped';
    });

    helpers.IsStartingHelper = Ember.Helper.helper(function([status]) {
        return status === 'starting';
    });

    helpers.IsStoppingHelper = Ember.Helper.helper(function([status]) {
        return status === 'stopping';
    });


    helpers.EqualHelper = Ember.Helper.helper(function(params) {
        return params[0] === params[1];
    });

    helpers.NotNullHelper = Ember.Helper.helper(function([param]) {
        return param !== null;
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
