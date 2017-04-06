define([
    'jsapi/v1/resources',
    './application_list_component',
    '../configurables',
    '../../urlutils'
], function(resources, application_list_component, configurables, urlutils) {
    "use strict";

    var Status = application_list_component.Status;

    // Ember component for the application VNC view

    var ApplicationViewComponent = Ember.Component.extend({
        tagName: 'section',

        init: function() {
            this._super(...arguments);

            this.set('iframe_width', 800);
            this.set('iframe_height', 600);
        },

        application_location: Ember.computed('application.app_data', function() {
            return urlutils.path_join(
                window.apidata.base_url,
                "containers",
                this.get('application.app_data.container.url_id')
            );
        }),

        actions: {
            start_application() {
                this.set('application.status', Status.STARTING);

                var mapping_id = this.get('application.app_data.mapping_id');

                var self = this;
                resources.Container.create({
                    mapping_id: mapping_id//,
                    //configurables: {'resolution': '800x600'}
                }).done(function() {
                    /*ga("send", "event", {
                        eventCategory: "Application",
                        eventAction: "start",
                        eventLabel: image_name
                    });*/

                    resources.Application.retrieve(mapping_id)
                        .done(function(new_data) {
                            self.set('application.app_data', new_data);
                            self.set('application.status', Status.RUNNING);
                        })
                        .fail(function(error) {
                            self.set('application.status', Status.STOPPED);
                            // dialogs.webapi_error_dialog(error);
                        });
                }).fail(function(error) {
                    self.set('application.status', Status.STOPPED);
                    // dialogs.webapi_error_dialog(error);
                });
            }
        }
    });

    return {
        ApplicationViewComponent: ApplicationViewComponent
    };
});
