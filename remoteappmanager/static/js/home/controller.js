/*globals: require, console*/
require([
    'jquery',
    'utils',
    'urlutils',
    'home/components/application_list_component',
    'home/components/application_view_component',
    'home/helpers'
], function(
    $,
    utils,
    urlutils,
    application_list_component,
    application_view_component,
    helpers) {
    'use strict';
    var Status = application_list_component.Status;

    var load_template = function(name) {
        var template_location = urlutils.path_join(
            window.apidata.base_url,
            'static/js/home/templates',
            name + '.hbs'
        );
        var template_name = name === 'application' ? name: 'components/' + name;
        return $.get(template_location, function(template) {
            Ember.TEMPLATES[template_name] = Ember.Handlebars.compile(template);
        });
    };

    // Load templates
    var load_templates = [
        load_template('application'),
        load_template('application-list'),
        load_template('application-view')
    ];

    utils.all(load_templates).done(function() {
        // Ember Application
        var AppList = Ember.Application.create({
            rootElement: '#ember_container'
        });

        // Add Ember helpers to the application
        Object.keys(helpers).forEach(function(key) {
            AppList[key] = helpers[key];
        });

        // Ember Controller
        AppList.ApplicationController = Ember.Controller.extend({
            init: function() {
                this._super(arguments);

                this.set('current_application', null);
                this.set('delayed', true);
            },

            actions: {
                toggle_app_selected: function(application) {
                    this.set('delayed', application.status !== Status.RUNNING);
                    this.set('current_application', application);
                }
            }
        });

        AppList.ApplicationListComponent =
            application_list_component.ApplicationListComponent;

        AppList.ApplicationViewComponent =
            application_view_component.ApplicationViewComponent;
    });
});
