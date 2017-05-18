let gamodule = require("gamodule");
let models = require("./models");
let ApplicationListView = require("./vue-components/ApplicationListView");
let ApplicationView = require("./vue-components/ApplicationView");
require("filters");

// This model keeps the retrieved content from the REST query locally.
// It is only synchronized at initial load.
let model = new models.ApplicationListModel();

// Initialize views
let appListView = new ApplicationListView({
  el: '#applist',
  data: function() { return { model: model }; }
});

let appView = new ApplicationView({
  el: '#appview',
  data: function() { return { model: model }; }
});

// Create GA observer
let gaObserver = new gamodule.GaObserver();

appView.$on('startApplication', function(application) {
  gaObserver.triggerApplicationStarting(application.appData.image.name);
});

appListView.$on('entryClicked', function() { appView.focusIframe(); });

model.update();
