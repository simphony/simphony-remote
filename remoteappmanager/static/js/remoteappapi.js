define(['jquery', 'utils'], function ($, utils) {
    "use strict";

    var RemoteAppAPI = function (base_url) {
        // Object representing the interface to the Web API.
        // @param base_url : the url at which to find the web API endpoint.
        this.base_url = base_url;
    };
    
    var default_options = {
        type: 'GET',
        contentType: "application/json",
        cache: false,
        dataType : null, 
        processData: false,
        success: null,
        error: null
    };
   
    var ajax_defaults = function (options) {
        var d = {};
        utils.update(d, default_options);
        utils.update(d, options);
        return d;
    };
    
    RemoteAppAPI.prototype.start_application = function(id, configurables_data, options) {
        // Starts an application with a given id. (async)
        //
        // @param id : the mapping id of the application to start.
        // @param configurables: a dictionary of values to configure the
        //                       image startup according to its startup 
        //                       configurability options.
        // @param options : the options for the request. Optional.
        // @return a deferred object for the request.
        configurables_data = configurables_data || {};
        options = options || {};
        options = utils.update(options, {
            type: 'POST', 
            data: JSON.stringify({
                mapping_id: id,
                configurables: configurables_data
            })});
        return this._api_request(
            'containers',
            options
        );
    };

    RemoteAppAPI.prototype.stop_application = function (id, options) {
        // Stops an application with a given container id. (async)
        //
        // @param id : the container id of the started application.
        //             Note that this is different from the mapping id.
        // @param options : the options for the request. Optional. 
        // @return a deferred object for the request.
        options = options || {};
        options = utils.update(options, {type: 'DELETE'});
        return this._api_request(
            utils.url_path_join('containers', id),
            options
        );
    };

    RemoteAppAPI.prototype.available_applications = function (options) {
        // Requests the available applications. (async)
        //
        // @param options : the options for the request. Optional. 
        // @return a deferred object for the request.
        options = options || {};
        return this._api_request(
            utils.url_path_join('applications'),
            options
        );
    };
    
    RemoteAppAPI.prototype.application_info = function (id, options) {
        // Requests a given application information via its mapping id 
        // (name, icon, etc). (async)
        //
        // @param id : the mapping id of the application to start.
        // @param options : the options for the request. Optional. 
        // @return a deferred object for the request.
        options = options || {};
        return this._api_request(
            utils.url_path_join('applications', id),
            options
        );
    };

    RemoteAppAPI.prototype.available_applications_info = function (options) {
        // Retrieve information from the various applications and
        // connect the cascading callbacks.
        // Returns a single promise. When resolved, the attached 
        // callbacks will be passed an array of the promises for the various
        // retrieve operations, successful or not.
        var promise = $.Deferred();
        var self = this;

        $.when(self.available_applications(options))
            .done(function (response) {
                var request, requests = [];

                for (var i = 0; i < response.items.length; i++) {
                    // We neutralize the potential error from a jXHR request
                    // and make sure that all our requests "succeed" so that
                    // all/when can guarantee everything is done.
                    request = $.Deferred();

                    // These will go out of scope but they are still alive
                    // and performing to completion
                    self.application_info(response.items[i]).always(
                        request.resolve);

                    requests.push(request);
                }

                utils.all(requests)
                    .done(function (promises) {
                        // Fills the local application model with the results of the
                        // retrieve promises.
                        var data = [];
                        for (var i = 0; i < promises.length; i++) {
                            var result = promises[i];
                            if (result[2].status === 200) {
                                data.push(result[0]);
                            }
                        }
                        promise.resolve(data);
                    });
            
            })
            .fail(function() {
                promise.resolve([]);
            });
                
        return promise;
    };

    // Private
    RemoteAppAPI.prototype._api_request = function (path, options) {
        // Performs a request to the final endpoint
        // @param path : the relative path of the endpoint
        // @param options : the options for the request. Optional. 
        // @return a deferred object for the request.
        options = options || {};
        options = ajax_defaults(options || {});
        var url = utils.url_path_join(
                this.base_url,
                'api',
                'v1',
                utils.encode_uri_components(path)
            )+'/';

        return $.ajax(url, options);
    };

    return RemoteAppAPI;
});
