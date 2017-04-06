/*globals: require, console*/
require([
    "analytics",
    "home/components/application_list_component",
    "home/components/application_view_component",
    "home/helpers",
], function(
    analytics,
    application_list_component,
    application_view_component,
    helpers) {
    "use strict";
    var Status = application_list_component.Status;

    var ga = analytics.init();

    // Ember Application

    var AppList = Ember.Application.create({
        LOG_TRANSITIONS: true, // For debug
        rootElement: '#ember_container'
    });

    // Add Ember helpers to the application

    Object.keys(helpers).forEach(function(key) {
        AppList[key] = helpers[key];
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
