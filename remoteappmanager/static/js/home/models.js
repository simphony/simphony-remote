define([
    'jquery',
    'home/configurables',
    'utils',
    'jsapi/v1/resources'
], function ($, configurables, utils, resources) {
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
            .done(function (ids) {
                // We neutralize the potential error from a jXHR request
                // and make sure that all our requests "succeed" so that
                // all/when can guarantee everything is done.

                // These will go out of scope but they are still alive
                // and performing to completion
                var requests = [];
                for (var i = 0; i < ids.length; i++) {
                    requests.push($.Deferred());
                }

                // We need to bind with the current i index in the loop
                // Hence we create these closures to grab the index for
                // each new index
                var done_callback = function(index) {
                    return function(rep) {
                        requests[index].resolve(rep);
                    };
                };
                var fail_callback = function(index) {
                    return function() {
                        requests[index].resolve(null);
                    };
                };

                for (i = 0; i < ids.length; i++) {
                    var id = ids[i];
                    resources.Application.retrieve(id)
                        .done(done_callback(i))
                        .fail(fail_callback(i));

                }

                utils.all(requests)
                    .done(function (promises) {
                        // Fills the local application model with the results of the
                        // retrieve promises.
                        var data = [];
                        for (var i = 0; i < promises.length; i++) {
                            var result = promises[i];
                            if (result !== null) {
                                data.push(result);
                            }
                        }
                        promise.resolve(data);
                    });

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
        this.app_list[index].configurables = {};

        image.configurables.forEach(function(tag) {
            // If this returns null, the tag has not been recognized
            // by the client. skip it and let the server deal with the
            // missing data, either by using a default or throwing
            // an error.
            var ConfigurableCls = configurables.from_tag(tag);

            if (ConfigurableCls !== null) {
                this.app_list[index].configurables[tag] = new ConfigurableCls();
            }
        }.bind(this));
    };

    ApplicationListModel.prototype._update_status = function(index) {
        var app_data = this.app_list[index].app_data;

        if (app_data.container === null) {
            this.app_list[index].status = Status.STOPPED;
        } else {
            this.app_list[index].status = Status.RUNNING;
        }
    };

    return {
        ApplicationListModel: ApplicationListModel,
        Status: Status
    };
});
