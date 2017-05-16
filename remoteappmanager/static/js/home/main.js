var gamodule = require("gamodule");
var models = require("./models");
var applicationListView = require("./views/application_list_view");
var applicationView = require("./views/application_view");
require("filters");

// This model keeps the retrieved content from the REST query locally.
// It is only synchronized at initial load.
var model = new models.ApplicationListModel();

// Initialize views
var appListView = new applicationListView.ApplicationListView({
    el: '#applist',
    data: function() { return { model: model }; }
});

var appView = new applicationView.ApplicationView({
    el: '#appview',
    data: function() { return { model: model }; }
});

// Create GA observer
var gaObserver = new gamodule.GaObserver();

appView.$on('startApplication', function(application) {
    gaObserver.triggerApplicationStarting(application.appData.image.name);
});

appListView.$on('entryClicked', function() { appView.focusIframe(); });

model.update();
