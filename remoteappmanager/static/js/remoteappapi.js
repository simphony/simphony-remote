define(['jquery', 'utils'], function ($, utils) {
    "use strict";

    var RemoteAppAPI = function (base_url) {
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
   
    var update = function (d1, d2) {
        $.map(d2, function (i, key) {
            d1[key] = d2[key];
        });
        return d1;
    };
    
    var ajax_defaults = function (options) {
        var d = {};
        update(d, default_options);
        update(d, options);
        return d;
    };
    
    RemoteAppAPI.prototype.api_request = function (path, options) {
        options = options || {};
        options = ajax_defaults(options || {});
        var url = utils.url_path_join(
            this.base_url,
            'api',
            'v1',
            utils.encode_uri_components(path)
        )+'/';
        
        $.ajax(url, options);
    };
    
    RemoteAppAPI.prototype.start_application = function(id, options) {
        options = options || {};
        options = update(options, {
            type: 'POST', 
            data: JSON.stringify({
                mapping_id: id
            })});
        this.api_request(
            'containers',
            options
        );
    };

    RemoteAppAPI.prototype.stop_application = function (id, options) {
        options = options || {};
        options = update(options, {type: 'DELETE'});
        this.api_request(
            utils.url_path_join('containers', id),
            options
        );
    };
    
    return RemoteAppAPI;
});
