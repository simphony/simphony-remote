define(['jquery'], function ($) {
    "use strict";

    var ApplicationListModel = function(remote_app_api) {
        this._appapi = remote_app_api;
        this.data = [];
    };

    ApplicationListModel.prototype.update = function() {
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
