let gamodule = require("gamodule");
let models = require("./models");
let applicationListView = require("./views/application_list_view");
let applicationView = require("./views/application_view");
require("filters");

// This model keeps the retrieved content from the REST query locally.
// It is only synchronized at initial load.
let model = new models.ApplicationListModel();

// Initialize views
let appListView = new applicationListView.ApplicationListView({
  el: '#applist',
  data: function() { return { model: model }; }
});

let appView = new applicationView.ApplicationView({
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
