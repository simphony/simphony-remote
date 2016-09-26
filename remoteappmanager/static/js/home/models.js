define(['jquery', 'home/configurables'], function ($, configurables) {
    "use strict";
    
    var ApplicationListModel = function(remote_app_api) {
        // (constructor) Model for the application list.
        // Parameters
        // remote_app_api : RemoteAppAPI
        // The remote application API stub object
        this._appapi = remote_app_api;
        
        // Contains the data retrieved from the remote API
        this.app_data = [];
        
        // Contains the submodels for the configurables.
        // The values are aligned to the app_data index, and contain
        // a dictionary that maps a supported (by the image) configurable tag 
        // to its client-side model.
        this.configurables = [];
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
            self.app_data = app_data;
            self.configurables = [];
            
            // Add the options for some image types
            for (var data_idx = 0; data_idx < self.app_data.length; ++data_idx) {
                var image = self.app_data[data_idx].image;
                self.configurables[data_idx] = {};
                
                for (var cfg_idx = 0; cfg_idx < image.configurables.length; ++cfg_idx) {
                    var tag = image.configurables[cfg_idx];
                    
                    // If this returns null, the tag has not been recognized
                    // by the client. skip it and let the server deal with the 
                    // missing data, either by using a default or throwing
                    // an error.
                    var configurable_model_cls = configurables.from_tag(tag);
                    
                    if (configurable_model_cls !== null) {
                        self.configurables[data_idx][tag] = new configurable_model_cls();
                    }
               }
            }
        });
    };
    
    return {
        ApplicationListModel: ApplicationListModel
    };
});
