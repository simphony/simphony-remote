define([
    "jquery",
    "home/configurables",
    "jsapi/v1/resources",
    "dialogs"
], function ($, configurables, resources, dialogs) {
    "use strict";

    var Status = {
        RUNNING: "RUNNING",
        STARTING: "STARTING",
        STOPPING: "STOPPING",
        STOPPED: "STOPPED"
    };

    var available_applications_info = function () {
        // Retrieve information from the various applications and
        // connect the cascading callbacks.
        // Returns a single promise. When resolved, the attached
        // callbacks will be passed an array of the promises for the various
        // retrieve operations, successful or not.
        // This routine will go away when we provide the representation data
        // inline with the items at tornado-webapi level.

        var promise = $.Deferred();

        resources.Application.items()
            .done(function (identifiers, items) {
                var result = [];
                Object.keys(items).forEach(function(key) {
                    result.push(items[key]);
                });
                promise.resolve(result);

            })
            .fail(function() {
                promise.resolve([]);
            });

        return promise;
    };

    var ApplicationListModel = function() {
        // (constructor) Model for the application list.
        this.app_list = [];

        // Selection index for when we click on one entry.
        // Should be the index of the selected app_data,
        // or null if no selection.
        this.selected_index = null;

        this.loading = true;
    };

    ApplicationListModel.prototype.update = function() {
        // Requests an update of the object internal data.
        // This method returns a jQuery Promise object.
        // When resolved, this.data will contain a list of the retrieved
        // data. Note that, in error conditions, this routine resolves
        // successfully in any case, and the data is set to empty list
        return $.when(
            available_applications_info()
        ).done(function (app_data) {
            // app_data contains the data retrieved from the remote API

            var app_list = [];

            // Sort application list by names
            app_data.sort(function(app1, app2) {
                var app1_name = app1.image.ui_name? app1.image.ui_name: app1.image.name;
                var app2_name = app2.image.ui_name? app2.image.ui_name: app2.image.name;
                return app1_name < app2_name? -1: 1;
            });

            // Add the options for some image types
            app_data.forEach(function(application_data) {
                var app = {
                    app_data: application_data,
                    // Default values, will be overwritten
                    status: Status.STOPPED,
                    delayed: true,
                    configurables: [],
                    is_running: function() {return this.status === Status.RUNNING;},
                    is_stopped: function() {return this.status === Status.STOPPED;},
                    is_starting: function() {return this.status === Status.STARTING;},
                    is_stopping: function() {return this.status === Status.STOPPING;}
                };

                this._update_configurables(app);
                this._update_status(app);

                app.delayed = !app.is_running();
                app_list.push(app);
            }.bind(this));

            this.app_list = app_list;

            if(app_list.length) {this.selected_index = 0;}

            this.loading = false;
        }.bind(this));
    };

    ApplicationListModel.prototype.update_idx = function(index) {
        // Refetches and updates the entry at the given index.
        var app = this.app_list[index];
        var mapping_id = app.app_data.mapping_id;

        return resources.Application.retrieve(mapping_id)
        .done(function(new_data) {
            app.app_data = new_data;

            this._update_status(app);
        }.bind(this));
    };

    ApplicationListModel.prototype._update_configurables = function(app) {
        // Contains the submodels for the configurables.
        // It is a dictionary that maps a supported (by the image) configurable tag
        // to its client-side model.
        app.configurables = [];

        app.app_data.image.configurables.forEach(function(conf_name) {
            // If this returns null, the tag has not been recognized
            // by the client. skip it and let the server deal with the
            // missing data, either by using a default or throwing
            // an error.
            var configurable = configurables[conf_name];

            if (configurable !== undefined) {
                app.configurables.push(new configurables[conf_name]());
            }
        });
    };

    ApplicationListModel.prototype._update_status = function(app) {
        if (app.app_data.container === undefined) {
            app.status = Status.STOPPED;
        } else {
            app.status = Status.RUNNING;
        }
    };

    ApplicationListModel.prototype.start_application = function() {
        var selected_index = this.selected_index;
        var current_app = this.app_list[selected_index];

        current_app.status = Status.STARTING;
        current_app.delayed = true;

        var configurables_data = {};
        current_app.configurables.forEach(function(configurable) {
            configurables_data[configurable.tag] = configurable.as_config_dict();
        });

        resources.Container.create({
            mapping_id: current_app.app_data.mapping_id,
            configurables: configurables_data
        }).done(function() {
            this.update_idx(selected_index)
            .fail(function(error) {
                current_app.status = Status.STOPPED;
                dialogs.webapi_error_dialog(error);
            });
        }.bind(this)).fail(function(error) {
            current_app.status = Status.STOPPED;
            dialogs.webapi_error_dialog(error);
        });
    };

    ApplicationListModel.prototype.stop_application = function(index) {
        var app_stopping = this.app_list[index];
        app_stopping.status = Status.STOPPING;

        var url_id = app_stopping.app_data.container.url_id;

        resources.Container.delete(url_id)
        .done(function() {
            this.update_idx(index)
            .fail(function(error) {
                app_stopping.status = Status.STOPPED;
                dialogs.webapi_error_dialog(error);
            });
        }.bind(this))
        .fail(function(error) {
            app_stopping.status = Status.STOPPED;
            dialogs.webapi_error_dialog(error);
        });
    };

    return {
        ApplicationListModel: ApplicationListModel
    };
});
