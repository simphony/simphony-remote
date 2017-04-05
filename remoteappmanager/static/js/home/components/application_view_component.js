define([], function() {
    "use strict";

    // Ember component for the application VNC view

    var ApplicationViewComponent = Ember.Component.extend({
        tagName: 'section',
        disabled: false,

        actions: {
            start_button_clicked() {
                this.set('application_status', 'running');
            }
        }
    });

    return {
        ApplicationViewComponent: ApplicationViewComponent
    };
});
