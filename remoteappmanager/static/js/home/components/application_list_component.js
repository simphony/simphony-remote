define([
    '../applications_info',
    'jsapi/v1/resources',
    '../../dialogs'
], function(applications_info, resources, dialogs) {
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

    var Application = Ember.Object.extend({
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
            this._super(arguments);

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
                    this.get('application_entry_list').pushObject(
                        Application.create({
                            app_data: app_data[i],
                            status: (
                                app_data[i].container !== null ?
                                Status.RUNNING :
                                Status.STOPPED
                            ),
                            resolution: 'Window'
                        })
                    );
                }

                this.set('list_loading', false);
            }.bind(this));
        },

        actions: {
            toggle_app_clicked: function(index) {
                this.set('selected_app', index);

                // Send the action to the controller
                this.sendAction(
                    'update_current_app',
                    this.get('application_entry_list').objectAt(index)
                );
            },
            toggle_app_stopped: function(application) {
                application.set('status', Status.STOPPING);

                var url_id = application.get('app_data.container.url_id');

                resources.Container.delete(url_id)
                .done(function () {
                    var mapping_id = application.get('app_data.mapping_id');

                    return resources.Application.retrieve(mapping_id)
                    .done(function(new_data) {
                        application.set('status', Status.STOPPED);
                        application.set('app_data', new_data);
                    })
                    .fail(function(error) {
                        application.set('status', Status.STOPPED);
                        dialogs.webapi_error_dialog(error);
                    });
                })
                .fail(function (error) {
                    application.set('status', Status.STOPPED);
                    dialogs.webapi_error_dialog(error);
                });
            }
        },

        didInsertElement: function() {
            this._super(arguments);
            // Load AdminLTE Javascript (Temporary)
            require([window.AdminLTEJavascriptPath]);
        }
    });

    return {
        ApplicationListComponent : ApplicationListComponent,
        Status: Status
    };
});
