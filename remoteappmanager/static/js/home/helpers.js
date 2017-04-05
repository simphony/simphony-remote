define([
    "urlutils",
], function(urlutils) {
    "use strict";

    // Ember Helpers

    var IconSrcHelper = Ember.Helper.helper(function([app_data]) {
        var icon_data = app_data.image.icon_128;
        return (
            icon_data ?
            "data:image/png;base64," + icon_data :
            urlutils.path_join(
                this.base_url, "static", "images", "generic_appicon_128.png"
            )
        );
    });

    var AppNameHelper = Ember.Helper.helper(function([app_data]) {
        return (
            app_data.image.ui_name ?
            app_data.image.ui_name :
            app_data.image.name
        );
    });

    var IsRunningHelper = Ember.Helper.helper(function([status]) {
        return status === 'running';
    });

    var EqualHelper = Ember.Helper.helper(function(params) {
        return params[0] === params[1];
    });

    var NotNullHelper = Ember.Helper.helper(function([param]) {
        return param !== null;
    });

    return {
        IconSrcHelper: IconSrcHelper,
        AppNameHelper: AppNameHelper,
        IsRunningHelper: IsRunningHelper,
        EqualHelper: EqualHelper,
        NotNullHelper: NotNullHelper
    };
});
