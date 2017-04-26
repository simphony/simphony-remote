define([
    'jquery',
    'home/configurables',
    'utils',
    'jsapi/v1/resources'
], function ($, configurables, utils, resources) {
    "use strict";

    var Status = utils.Status;

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

            // Add the options for some image types
            app_data.forEach(function(application_data, data_idx) {
                this.app_list[data_idx] = { app_data: application_data };

                this._update_configurables(data_idx);
                this._update_status(data_idx);

                if (this.app_list[data_idx].status === Status.RUNNING) {
                    this.app_list[data_idx].delayed = false;
                } else {
                    this.app_list[data_idx].delayed = true;
                }
            }.bind(this));
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

    return {
        ApplicationListModel: ApplicationListModel
    };
});
