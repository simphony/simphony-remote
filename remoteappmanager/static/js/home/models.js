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
            .done(function (identifiers, items) {
                var result = [];
                for (var key in items) {
                    if (!items.hasOwnProperty(key)) {
                        continue;
                    }
                    result.push(items[key]);
                }
                promise.resolve(result);
            })
            .fail(function() {
                promise.resolve([]);
            });

        return promise;
    };

    var ApplicationListModel = function() {
        // (constructor) Model for the application list.
        
        // Contains the data retrieved from the remote API
        this.app_data = [];
        
        // Contains the submodels for the configurables.
        // The values are aligned to the app_data index, and contain
        // a dictionary that maps a supported (by the image) configurable tag 
        // to its client-side model.
        this.configurables = [];
        
        // Selection index for when we click on one entry.
        // Should be the index of the selected app_data, 
        // or null if no selection.
        this.selected_index = null;
        
        // indexes currently starting
        this.status = [];
    };

    ApplicationListModel.prototype.update = function() {
        // Requests an update of the object internal data.
        // This method returns a jQuery Promise object. 
        // When resolved, this.data will contain a list of the retrieved
        // data. Note that, in error conditions, this routine resolves
        // successfully in any case, and the data is set to empty list
        var self = this;
        
        return $.when(
            available_applications_info()
        ).done(function (app_data) {
            self.app_data = app_data;
            self.configurables = [];
            
            // Add the options for some image types
            for (var data_idx = 0; data_idx < self.app_data.length; ++data_idx) {
                self._update_configurables(data_idx);
                self._update_status(data_idx);
            }
        });
    };

    ApplicationListModel.prototype.update_idx = function(index) {
        // Refetches and updates the entry at the given index.
        var self = this;
        
        var entry = this.app_data[index];
        var mapping_id = entry.mapping_id;
        return resources.Application.retrieve(mapping_id)
            .done(function(new_data) {
                self.app_data[index] = new_data;
                self._update_configurables(index);
                self._update_status(index);
            });
    };

    ApplicationListModel.prototype._update_configurables = function(index) {
        // Updates the configurables submodel for a given application index.
        var self = this;
        var image = self.app_data[index].image;
        self.configurables[index] = {};

        for (var cfg_idx = 0; cfg_idx < image.configurables.length; ++cfg_idx) {
            var tag = image.configurables[cfg_idx];

            // If this returns null, the tag has not been recognized
            // by the client. skip it and let the server deal with the 
            // missing data, either by using a default or throwing
            // an error.
            var ConfigurableCls = configurables.from_tag(tag);

            if (ConfigurableCls !== null) {
                self.configurables[index][tag] = new ConfigurableCls();
            }
        }
    };
  
    ApplicationListModel.prototype._update_status = function(index) {
        var self = this;
        var app_data = self.app_data[index];
        
        if (app_data.container === undefined) {
            self.status[index] = Status.STOPPED;
        } else {
            self.status[index] = Status.RUNNING;
        }
    };
   
    return {
        ApplicationListModel: ApplicationListModel,
        Status: Status
    };
});
