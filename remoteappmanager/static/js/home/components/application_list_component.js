define([
    '../applications_info',
    '../configurables'
], function(applications_info, configurables) {
    "use strict";
    var available_applications_info =
        applications_info.available_applications_info;

    var Status = {
        RUNNING: "running",
        STARTING: "starting",
        STOPPING: "stopping",
        STOPPED: "stopped"
    };

    // Ember application model

    const Application = Ember.Object.extend({
        //
    });

    // Ember component for the application list

    var ApplicationListComponent = Ember.Component.extend({
        tagName: 'ul',

        empty_list: Ember.computed(
            'application_entry_list', 'list_loading',
            function() {
                return this.get('application_entry_list').length === 0 &&
                    this.get('list_loading') !== true;
            }
        ),

        init: function() {
            this._super(...arguments);

            this.app_data = null; // Not an Ember Object

            this.set('list_loading', true);
            this.set('selected_app', null);
            this.set('application_entry_list', []);

            this.fill_list();
        },

        fill_list: function() {
            return $.when(
                available_applications_info()
            ).done(function (app_data) {
                this.app_data = app_data;

                var num_entries = app_data.length;

                // Add the options for some image types
                for (var i = 0; i < num_entries; ++i) {
                    this._update_application(i);
                }

                this.set('list_loading', false);
            }.bind(this));
        },

        _update_application: function(index) {
            // Updates the configurables submodel for a given application index.
            var app_data = this.app_data[index];
            var image = app_data.image;
            var status = app_data.container !== null ?
                Status.RUNNING :
                Status.STOPPED;
            var configurable = {};

            for (var i = 0; i < image.configurables.length; ++i) {
                var tag = image.configurables[i];

                // If this returns null, the tag has not been recognized
                // by the client. skip it and let the server deal with the
                // missing data, either by using a default or throwing
                // an error.
                var ConfigurableCls = configurables.from_tag(tag);

                if (ConfigurableCls !== null) {
                    configurable[tag] = new ConfigurableCls();
                }
            }

            var app_object = Application.create({
                app_data: app_data,
                configurable: configurable,
                status: status
            });

            this.get('application_entry_list').pushObject(app_object);
        },

        actions: {
            toggle_app_clicked(index) {
                this.set('selected_app', index);

                console.log('(ApplicationListComponent) Application', index, 'selected');

                // Send the action to the controller
                this.sendAction(
                    'update_current_app',
                    this.get('application_entry_list').objectAt(index)
                );
            },
            toggle_app_stopped(application) {
                if (application.get('status') === Status.STOPPING) {
                    return;
                }

                application.set('status', Status.STOPPED);

                //TODO: Stop application
            }
        },

        didInsertElement() {
            this._super(...arguments);
            // Load AdminLTE Javascript (Temporary)
            require([window.AdminLTEJavascriptPath]);
        }
    });

    return {
        ApplicationListComponent : ApplicationListComponent,
        Status: Status
    };
});
