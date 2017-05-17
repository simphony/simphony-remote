let $ = require("jquery");
let resources = require("user-resources");
let configurables = require("./configurables");

let Status = {
    RUNNING: "RUNNING",
    STARTING: "STARTING",
    STOPPING: "STOPPING",
    STOPPED: "STOPPED"
};

let availableApplicationsInfo = function () {
    // Retrieve information from the letious applications and
    // connect the cascading callbacks.
    // Returns a single promise. When resolved, the attached
    // callbacks will be passed an array of the promises for the letious
    // retrieve operations, successful or not.
    // This routine will go away when we provide the representation data
    // inline with the items at tornado-webapi level.

    let promise = $.Deferred();

    resources.Application.items()
        .done((identifiers, items) => {
            let result = [];
            Object.keys(items).forEach((key) => {
                result.push(items[key]);
            });
            promise.resolve(result);

        })
        .fail(() => {
            promise.resolve([]);
        });

    return promise;
};


class ApplicationListModel {
    constructor() {
        this.appList = [];

        // Selection index for when we click on one entry.
        // Should be the index of the selected application,
        // or null if no application available (first app is clicked by default).
        this.selectedIndex = null;

        this.loading = true;
    }

    update() {
        // Requests an update of the object internal data.
        // This method returns a jQuery Promise object.
        // When resolved, this.data will contain a list of the retrieved
        // data. Note that, in error conditions, this routine resolves
        // successfully in any case, and the data is set to empty list
        return $.when(
            availableApplicationsInfo()
        ).done((appData) => {
            // appData contains the data retrieved from the remote API

            let appList = [];

            // Sort application list by names
            appData.sort((app1, app2) => {
                let app1Name = app1.image.ui_name? app1.image.ui_name: app1.image.name;
                let app2Name = app2.image.ui_name? app2.image.ui_name: app2.image.name;
                return app1Name < app2Name? -1: 1;
            });

            // Add the options for some image types
            appData.forEach((applicationData) => {
                let app = {
                    appData: applicationData,
                    // Default values, will be overwritten
                    status: Status.STOPPED,
                    // If true the user will see the loading spinner (when starting the application)
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
            });

            this.appList = appList;

            if(appList.length) {this.selectedIndex = 0;}

            this.loading = false;
        });
    }

    updateIdx(index) {
        // Refetches and updates the entry at the given index.
        let app = this.appList[index];
        let mapping_id = app.appData.mapping_id;

        return resources.Application.retrieve(mapping_id)
        .done((newData) => {
            app.appData = newData;

            this._updateStatus(app);
        });
    }

    _updateConfigurables(app) {
        // Contains the submodels for the configurables.
        // It is a dictionary that maps a supported (by the image) configurable tag
        // to its client-side model.
        app.configurables = [];

        app.appData.image.configurables.forEach(function(tag) {
            // If this returns null, the tag has not been recognized
            // by the client. skip it and let the server deal with the
            // missing data, either by using a default or throwing
            // an error.
            let ConfigurableCls = configurables[tag].model;

            if (ConfigurableCls !== undefined) {
                app.configurables.push(new ConfigurableCls());
            }
        });
    }

    _updateStatus(app) {
        if (app.appData.container === undefined) {
            app.status = Status.STOPPED;
        } else {
            app.status = Status.RUNNING;
        }
    }

    startApplication() {
        let selectedIndex = this.selectedIndex;
        let currentApp = this.appList[selectedIndex];

        currentApp.status = Status.STARTING;
        currentApp.delayed = true;

        let configurablesData = {};
        currentApp.configurables.forEach(function(configurable) {
            let tag = configurable.tag;
            configurablesData[tag] = configurable.asConfigDict();
        });

        let startPromise = $.Deferred();

        resources.Container.create({
            mapping_id: currentApp.appData.mapping_id,
            configurables: configurablesData
        })
        .done(() => {
            this.updateIdx(selectedIndex)
            .done(startPromise.resolve)
            .fail((error) => {
                currentApp.status = Status.STOPPED;
                startPromise.reject(error);
            });
        })
        .fail((error) => {
            currentApp.status = Status.STOPPED;
            startPromise.reject(error);
        });

        return startPromise;
    }

    stopApplication(index) {
        let appStopping = this.appList[index];
        appStopping.status = Status.STOPPING;

        let url_id = appStopping.appData.container.url_id;

        let stopPromise = $.Deferred();

        resources.Container.delete(url_id)
        .done(() => {
            this.updateIdx(index)
            .done(stopPromise.resolve)
            .fail(function(error) {
                appStopping.status = Status.STOPPED;
                stopPromise.reject(error);
            });
        })
        .fail((error) => {
            appStopping.status = Status.STOPPED;
            stopPromise.reject(error);
        });

        return stopPromise;
    }
}

module.exports = {
    ApplicationListModel
};
