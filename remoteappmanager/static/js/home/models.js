define([
    'jquery',
    'home/configurables',
    'utils',
    'jsapi/v1/resources',
    "gamodule",
    "dialogs"
], function ($, configurables, utils, resources, gamodule, dialogs) {
    "use strict";

    var Status = utils.Status;
    var ga = gamodule.init();

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

            this.app_list = [];

            // Sort application list by names
            app_data.sort(function(app1, app2) {
                var app1_name = app1.image.ui_name? app1.image.ui_name: app1.image.name;
                var app2_name = app2.image.ui_name? app2.image.ui_name: app2.image.name;
                return app1_name < app2_name? -1: 1;
            });

            // Add the options for some image types
            app_data.forEach(function(application_data, data_idx) {
                this.app_list.push({
                    app_data: application_data,
                    // Default values, will be overwritten
                    status: Status.STOPPED,
                    delayed: true,
                    configurables: []
                });

                this._update_configurables(data_idx);
                this._update_status(data_idx);

                if (this.app_list[data_idx].status === Status.RUNNING) {
                    this.app_list[data_idx].delayed = false;
                } else {
                    this.app_list[data_idx].delayed = true;
                }
            }.bind(this));

            this.loading = false;
        }.bind(this));
    };

    ApplicationListModel.prototype.update_idx = function(index) {
        // Refetches and updates the entry at the given index.
        var entry = this.app_list[index].app_data;
        var mapping_id = entry.mapping_id;

        return resources.Application.retrieve(mapping_id)
        .done(function(new_data) {
            this.app_list[index].app_data = new_data;

            this._update_configurables(index);
            this._update_status(index);
        }.bind(this));
    };

    ApplicationListModel.prototype._update_configurables = function(index) {
        // Updates the configurables submodel for a given application index.
        var image = this.app_list[index].app_data.image;

        // Contains the submodels for the configurables.
        // It is a dictionary that maps a supported (by the image) configurable tag
        // to its client-side model.
        this.app_list[index].configurables = [];

        image.configurables.forEach(function(tag) {
            // If this returns null, the tag has not been recognized
            // by the client. skip it and let the server deal with the
            // missing data, either by using a default or throwing
            // an error.
            var ConfigurableCls = configurables.from_tag(tag);

            if (ConfigurableCls !== null) {
                this.app_list[index].configurables.push(new ConfigurableCls());
            }
        }.bind(this));
    };

    ApplicationListModel.prototype._update_status = function(index) {
        var app_data = this.app_list[index].app_data;

        if (app_data.container === undefined) {
            this.app_list[index].status = Status.STOPPED;
        } else {
            this.app_list[index].status = Status.RUNNING;
        }
    };

    ApplicationListModel.prototype.start_application = function() {
        var selected_index = this.selected_index;
        var current_app = this.app_list[selected_index];

        current_app.status = Status.STARTING;
        current_app.delayed = true;

        var configurables_data = {};
        current_app.configurables.forEach(function(configurable) {
            var tag = configurable.tag;
            configurables_data[tag] = configurable.as_config_dict();
        });

        resources.Container.create({
            mapping_id: current_app.app_data.mapping_id,
            configurables: configurables_data
        }).done(function() {
            ga("send", "event", {
                eventCategory: "Application",
                eventAction: "start",
                eventLabel: current_app.app_data.image.name
            });

            this.update_idx(selected_index)
            .fail(function(error) {
                current_app.status = Status.STOPPED;
                dialogs.webapi_error_dialog(error);
            });
        }.bind(this)).fail(function(error) {
            current_app.status = Status.STOPPED;
            dialogs.webapi_error_dialog(error);
        });
    }

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
    }

    return {
        ApplicationListModel: ApplicationListModel
    };
});
