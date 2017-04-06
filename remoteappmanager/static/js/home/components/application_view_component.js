define([
    'analytics',
    'jsapi/v1/resources',
    './application_list_component',
    '../../urlutils',
    '../../utils',
    '../../dialogs'
], function(
        analytics, resources, application_list_component, urlutils, utils, dialogs
    ) {
    'use strict';

    var ga = analytics.init();

    var Status = application_list_component.Status;

    var getWindowResolution = function() {
        var max_size = utils.max_iframe_size();
        return max_size[0]+"x"+max_size[1];
    };

    // Ember component for the application VNC view

    var ApplicationViewComponent = Ember.Component.extend({
        tagName: 'section',
        classNames: 'content',
        classNameBindings: ['noPadding'],
        resolution_options: [
            'Window', '1920x1080', '1280x1024', '1280x800', '1024x768'
        ],

        init: function() {
            this._super(...arguments);

            // Default resolution is the Window size
            this.set('resolution', 'Window');
        },

        noPadding: Ember.computed('application.status', function() {
            var app_status = this.get('application.status');
            return !(
                app_status === Status.STOPPED || app_status === Status.STARTING
            );
        }),

        application_location: Ember.computed('application.app_data', function() {
            return urlutils.path_join(
                window.apidata.base_url,
                'containers',
                this.get('application.app_data.container.url_id')
            );
        }),

        iframe_style: Ember.computed('resolution', 'application.status', function() {
            var resolution = this.get('resolution');
            if(resolution === 'Window') { resolution = getWindowResolution(); }

            var size = resolution.split('x');

            return Ember.String.htmlSafe(
                'min-width:'+size[0]+'px;'+
                'min-height:'+size[1]+'px;'
            );
        }),

        actions: {
            start_application() {
                this.set('application.status', Status.STARTING);

                var mapping_id = this.get('application.app_data.mapping_id');

                var resolution = this.get('resolution');
                if(resolution === 'Window') { resolution = getWindowResolution(); }

                var current_application = this.get('application');
                resources.Container.create({
                    mapping_id: mapping_id,
                    configurables: {'resolution': {'resolution': resolution}}
                }).done(function() {
                    ga('send', 'event', {
                        eventCategory: 'Application',
                        eventAction: 'start',
                        eventLabel: current_application.get('app_data.image.name')
                    });

                    resources.Application.retrieve(mapping_id)
                        .done(function(new_data) {
                            current_application.set('app_data', new_data);
                            current_application.set('status', Status.RUNNING);
                        })
                        .fail(function(error) {
                            current_application.set('status', Status.STOPPED);
                            dialogs.webapi_error_dialog(error);
                        });
                }).fail(function(error) {
                    current_application.set('status', Status.STOPPED);
                    dialogs.webapi_error_dialog(error);
                });
            },

            toggle_resolution_changed: function(event) {
                this.set('resolution', event.target.value);
            }
        }
    });

    return {
        ApplicationViewComponent: ApplicationViewComponent
    };
});
