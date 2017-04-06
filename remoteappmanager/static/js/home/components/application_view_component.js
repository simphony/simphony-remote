define([
    'analytics',
    'jsapi/v1/resources',
    './application_list_component',
    '../../urlutils',
    '../../utils'
], function(
        analytics, resources, application_list_component, urlutils, utils
    ) {
    'use strict';

    var ga = analytics.init();

    var Status = application_list_component.Status;

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
            var max_size = utils.max_iframe_size();
            this.set('resolution', max_size[0]+"x"+max_size[1]);
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

        width: Ember.computed('resolution', function() {
            return this.get('resolution').split('x')[0];
        }),

        height: Ember.computed('resolution', function() {
            return this.get('resolution').split('x')[1];
        }),

        actions: {
            start_application() {
                this.set('application.status', Status.STARTING);

                var mapping_id = this.get('application.app_data.mapping_id');

                var current_application = this.get('application');
                resources.Container.create({
                    mapping_id: mapping_id,
                    configurables: {'resolution': {'resolution': this.get('resolution')}}
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
                            // dialogs.webapi_error_dialog(error);
                        });
                }).fail(function(error) {
                    current_application.set('status', Status.STOPPED);
                    // dialogs.webapi_error_dialog(error);
                });
            },

            toggle_resolution_changed: function(event) {
                var value = event.target.value;

                if(value === 'Window') {
                    var max_size = utils.max_iframe_size();
                    this.set('resolution', max_size[0]+"x"+max_size[1]);
                } else {
                    this.set('resolution', value);
                }
            }
        }
    });

    return {
        ApplicationViewComponent: ApplicationViewComponent
    };
});
