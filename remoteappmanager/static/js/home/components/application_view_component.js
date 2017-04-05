define([], function() {
    "use strict";

    // Ember component for the application VNC view

    var ApplicationViewComponent = Ember.Component.extend({
        tagName: 'section',
        disabled: false,
        current_application: null,

        update: function(){
            console.log('(ApplicationView) Changing to app', this.get('current_application'))
        }.observes('current_application'),
    });

    return {
        ApplicationViewComponent: ApplicationViewComponent
    };
});
