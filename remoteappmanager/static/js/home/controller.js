/*globals: require, console*/
require([
    "jquery",
    "urlutils",
    "analytics",
    "home/models",
    "home/components/application_list_component",
    "home/components/application_view_component",
    "jsapi/v1/resources",
    'utils',
], function(
    $,
    urlutils,
    analytics,
    models,
    application_list_component,
    application_view_component,
    resources,
    utils,
    configurables) {
    "use strict";
    var Status = application_list_component.Status;

    var ga = analytics.init();

    // Ember Application

    var AppList = Ember.Application.create({
        LOG_TRANSITIONS: true, // For debug
        rootElement: '#ember_container'
    });

    // Ember Helpers

    AppList.IconSrcHelper = Ember.Helper.helper(function([app_data]) {
        var icon_data = app_data.image.icon_128;
        return (
            icon_data ?
            "data:image/png;base64," + icon_data :
            urlutils.path_join(
                this.base_url, "static", "images", "generic_appicon_128.png"
            )
        );
    });

    AppList.AppNameHelper = Ember.Helper.helper(function([app_data]) {
        return (
            app_data.image.ui_name ?
            app_data.image.ui_name :
            app_data.image.name
        );
    });

    AppList.IsRunningHelper = Ember.Helper.helper(function([status]) {
        return status === Status.RUNNING.toLowerCase();
    });

    AppList.EqualHelper = Ember.Helper.helper(function(params) {
        return params[0] === params[1];
    });

    AppList.NotNullHelper = Ember.Helper.helper(function([param]) {
        return param !== null;
    });

    // Ember Controller

    AppList.ApplicationController = Ember.Controller.extend({
        init: function() {
            this._super(...arguments);

            this.set('current_application', null);
        },

        actions: {
            toggle_app_selected(application) {
                console.log('(Controller) App selected:', application);
                this.set('current_application', application);
            }
        }
    });

    AppList.ApplicationListComponent =
        application_list_component.ApplicationListComponent;

    AppList.ApplicationViewComponent =
        application_view_component.ApplicationViewComponent;

});
