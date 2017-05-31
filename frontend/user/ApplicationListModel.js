let configurables = require("./configurables/configurables");
let JsonApi = require("devour-client");
let urlUtils = require("urlutils");

const jsonApi = new JsonApi({
  apiUrl: urlUtils.pathJoin(window.apidata.base_url, 'api', 'v2'),
  trailingSlash: {resource: false, collection: true}
});

jsonApi.define('applications', {
  image: {
    jsonApi: 'hasOne',
    type: 'image'
  },
  container: {
    jsonApi: 'hasOne',
    type: 'container'
  }
});
jsonApi.define('image', {
  name: '',
  ui_name: '',
  icon_128: '',
  description: '',
  policy: {
    jsonApi: 'hasOne',
    type: 'policy'
  },
  configurables: []
});
jsonApi.define('policy', {
  allow_home: true,
  volume_source: '',
  volume_target: '',
  volume_mode: ''
});
jsonApi.define('container', {});

let Status = {
  RUNNING: "RUNNING",
  STARTING: "STARTING",
  STOPPING: "STOPPING",
  STOPPED: "STOPPED"
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
    // When resolved, this.data will contain a list of the retrieved
    // data. Note that, in error conditions, this routine resolves
    // successfully in any case, and the data is set to empty list
    return jsonApi.findAll('applications').then(appData => {
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
    let id = app.appData.id;

    return jsonApi.find('application', id)
    .then(newData => {
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
      let ConfigurableCls = configurables[tag];

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

    let startPromise = new Promise(resolve => { resolve(); });

    jsonApi.one('application', currentApp.appData.id).one('container').post({
      id: currentApp.appData.id,
      configurables: configurablesData
    })
    .then(() => {
      this.updateIdx(selectedIndex)
      .then(startPromise.resolve)
      .catch(error => {
        currentApp.status = Status.STOPPED;
        startPromise.reject(error);
      });
    })
    .catch(error => {
      currentApp.status = Status.STOPPED;
      startPromise.reject(error);
    });

    return startPromise;
  }

  stopApplication(index) {
    let appStopping = this.appList[index];
    appStopping.status = Status.STOPPING;

    let stopPromise = new Promise(resolve => { resolve(); });

    jsonApi.one('application', appStopping.appData.id).one('container').destroy()
    .then(() => {
      this.updateIdx(index)
      .then(stopPromise.resolve)
      .catch(error => {
        appStopping.status = Status.STOPPED;
        stopPromise.reject(error);
      });
    })
    .catch(error => {
      appStopping.status = Status.STOPPED;
      stopPromise.reject(error);
    });

    return stopPromise;
  }
}

module.exports = ApplicationListModel;
