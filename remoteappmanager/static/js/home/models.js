define([
    "jquery",
    "home/configurables",
    "jsapi/v1/resources"
], function ($, configurables, resources) {
    "use strict";

    var Status = {
        RUNNING: "RUNNING",
        STARTING: "STARTING",
        STOPPING: "STOPPING",
        STOPPED: "STOPPED"
    };

    var availableApplicationsInfo = function () {
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
        this.appList = [];

        // Selection index for when we click on one entry.
        // Should be the index of the selected application,
        // or null if no application available (first app is clicked by default).
        this.selectedIndex = null;

        this.loading = true;
    };

    ApplicationListModel.prototype.update = function() {
        // Requests an update of the object internal data.
        // This method returns a jQuery Promise object.
        // When resolved, this.data will contain a list of the retrieved
        // data. Note that, in error conditions, this routine resolves
        // successfully in any case, and the data is set to empty list
        return $.when(
            availableApplicationsInfo()
        ).done(function (appData) {
            // appData contains the data retrieved from the remote API

            var appList = [];

            // Sort application list by names
            appData.sort(function(app1, app2) {
                var app1Name = app1.image.ui_name? app1.image.ui_name: app1.image.name;
                var app2Name = app2.image.ui_name? app2.image.ui_name: app2.image.name;
                return app1Name < app2Name? -1: 1;
            });

            // Add the options for some image types
            appData.forEach(function(applicationData) {
                var app = {
                    appData: applicationData,
                    // Default values, will be overwritten
                    status: Status.STOPPED,
                    delayed: true,
                    configurables: [],
                    isRunning: function() {return this.status === Status.RUNNING;},
                    isStopped: function() {return this.status === Status.STOPPED;},
                    isStarting: function() {return this.status === Status.STARTING;},
                    isStopping: function() {return this.status === Status.STOPPING;}
                };

                this._updateConfigurables(app);
                this._updateStatus(app);

                app.delayed = !app.isRunning();
                appList.push(app);
            }.bind(this));

            this.appList = appList;

            if(appList.length) {this.selectedIndex = 0;}

            this.loading = false;
        }.bind(this));
    };

    ApplicationListModel.prototype.updateIdx = function(index) {
        // Refetches and updates the entry at the given index.
        var app = this.appList[index];
        var mapping_id = app.appData.mapping_id;

        return resources.Application.retrieve(mapping_id)
        .done(function(newData) {
            app.appData = newData;

            this._updateStatus(app);
        }.bind(this));
    };

    ApplicationListModel.prototype._updateConfigurables = function(app) {
        // Contains the submodels for the configurables.
        // It is a dictionary that maps a supported (by the image) configurable tag
        // to its client-side model.
        app.configurables = [];

        app.appData.image.configurables.forEach(function(tag) {
            // If this returns null, the tag has not been recognized
            // by the client. skip it and let the server deal with the
            // missing data, either by using a default or throwing
            // an error.
            var ConfigurableCls = configurables[tag];

            if (ConfigurableCls !== undefined) {
                app.configurables.push(new ConfigurableCls());
            }
        });
    };

    ApplicationListModel.prototype._updateStatus = function(app) {
        if (app.appData.container === undefined) {
            app.status = Status.STOPPED;
        } else {
            app.status = Status.RUNNING;
        }
    };

    ApplicationListModel.prototype.startApplication = function() {
        var selectedIndex = this.selectedIndex;
        var currentApp = this.appList[selectedIndex];

        currentApp.status = Status.STARTING;
        currentApp.delayed = true;

        var configurablesData = {};
        currentApp.configurables.forEach(function(configurable) {
            var tag = configurable.tag;
            configurablesData[tag] = configurable.asConfigDict();
        });

        var startPromise = $.Deferred();

        resources.Container.create({
            mapping_id: currentApp.appData.mapping_id,
            configurables: configurablesData
        })
        .done(function() {
            this.updateIdx(selectedIndex)
            .done(startPromise.resolve)
            .fail(function(error) {
                currentApp.status = Status.STOPPED;
                startPromise.reject(error);
            });
        }.bind(this))
        .fail(function(error) {
            currentApp.status = Status.STOPPED;
            startPromise.reject(error);
        });

        return startPromise;
    };

    ApplicationListModel.prototype.stopApplication = function(index) {
        var appStopping = this.appList[index];
        appStopping.status = Status.STOPPING;

        var url_id = appStopping.appData.container.url_id;

        var stopPromise = $.Deferred();

        resources.Container.delete(url_id)
        .done(function() {
            this.updateIdx(index)
            .done(stopPromise.resolve)
            .fail(function(error) {
                appStopping.status = Status.STOPPED;
                stopPromise.reject(error);
            });
        }.bind(this))
        .fail(function(error) {
            appStopping.status = Status.STOPPED;
            stopPromise.reject(error);
        });

        return stopPromise;
    };

    return {
        ApplicationListModel: ApplicationListModel
    };
});
