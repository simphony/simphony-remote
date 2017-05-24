let gamodule = require("gamodule");
let ErrorDialog = require("ErrorDialog");
let ApplicationListModel = require("./ApplicationListModel");
let ApplicationListView = require("./vue-components/ApplicationListView");
let ApplicationView = require("./vue-components/ApplicationView");
let ApplicationLabel = require("./vue-components/ApplicationLabel");
require("filters");

// This model keeps the retrieved content from the REST query locally.
// It is only synchronized at initial load.
let model = new ApplicationListModel();

let errorDialog = new ErrorDialog({
  el: '#error-dialog-container'
});

// Initialize views
let appListView = new ApplicationListView({
  el: '#applist',
  data: function() { return { model }; }
});

let appView = new ApplicationView({
  el: '#appview',
  data: function() { return { model }; }
});

let applabel = new ApplicationLabel({
  el: '#applabel',
  data: function() { return { model: model }; }
});

// Create GA observer
let gaObserver = new gamodule.GaObserver();

// Set events
appView.$on('startApplication', function(application) {
  gaObserver.triggerApplicationStarting(application.appData.image.name);
});

appView.$on('error', function(error) {
  errorDialog.errorList.push(error);
});

appListView.$on('entryClicked', function() { appView.focusIframe(); });

applabel.$on('error', function(error) {
  errorDialog.errorList.push(error);
});

model.update();
