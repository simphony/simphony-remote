define(['jquery'], function ($) {
    "use strict";

    var ApplicationListModel = function(remote_app_api) {
        // (constructor) Model for the application list.
        // Parameters
        // remote_app_api : RemoteAppAPI
        // The remote application API stub object
        this._appapi = remote_app_api;
        
        // Contains the data retrieved from the remote API
        this.data = [];
    };

    ApplicationListModel.prototype.update = function() {
        // Requests an update of the object internal data.
        // This method returns a jQuery Promise object. 
        // When resolved, this.data will contain a list of the retrieved
        // data. Note that, in error conditions, this routine resolves
        // successfully in any case, and the data is set to empty list
        var self = this;
        return $.when(
            self._appapi.available_applications_info()
        ).done(function (app_data) {
            self.data = app_data;
        });
    };
    
    return {
        ApplicationListModel: ApplicationListModel
    };
});
