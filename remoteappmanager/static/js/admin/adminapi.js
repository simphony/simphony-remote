define(['jquery', 'utils'], function ($, utils) {
    "use strict";

    var AdminAPI = function (base_url) {
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
    
    AdminAPI.prototype.stop_container = function (url_id, options) {
        // Stops a container by url id. (async)
        //
        // @param url_id : the url id of the started container.
        // @param options : the options for the request. Optional. 
        // @return a deferred object for the request.
        options = options || {};
        options = utils.update(options, {type: 'DELETE'});
        return this._api_request(
            utils.url_path_join('containers', url_id),
            options
        );
    };
    
    AdminAPI.prototype.remove_application = function (id, options) {
        options = options || {};
        options = utils.update(options, {type: 'DELETE'});
        return this._api_request(
            utils.url_path_join('applications', id),
            options
        );
    };
    
    AdminAPI.prototype.create_application = function (image_name, options) {
        options = options || {};
        options = utils.update(options, {
            type: 'POST',
            data: JSON.stringify({
                image_name: image_name
            })
        });
        return this._api_request(
            'applications',
            options
        );
    };

    // Private
    AdminAPI.prototype._api_request = function (path, options) {
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

    return {
        AdminAPI: AdminAPI
    };
});
