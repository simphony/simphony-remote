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

        application_location: Ember.computed('application_data', function() {
            return urlutils.path_join(
                window.apidata.base_url,
                "containers",
                this.get('application_data.container.url_id')
            );
        }),

        actions: {
            start_application() {
                this.set('application_status', Status.STARTING);

                var mapping_id = this.get('application_data.mapping_id');

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
                            self.set('application_data', new_data);
                            self.set('application_status', Status.RUNNING);
                        })
                        .fail(function(error) {
                            self.set('application_status', Status.STOPPED);
                            // dialogs.webapi_error_dialog(error);
                        });
                }).fail(function(error) {
                    self.set('application_status', Status.STOPPED);
                    // dialogs.webapi_error_dialog(error);
                });
            }
        }
    });

    return {
        ApplicationViewComponent: ApplicationViewComponent
    };
});
