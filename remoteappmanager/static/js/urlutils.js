// Based on IPython's base.js.utils
// Original Copyright (c) IPython Development Team.
// Distributed under the terms of the Modified BSD License.

// Modifications Copyright (c) Juptyer Development Team.
// Distributed under the terms of the Modified BSD License.

define([
    'jquery'
], function ($) {
    "use strict";

    var path_join = function () {
        // join a sequence of url components with '/'
        var url = '', i = 0;

        for (i = 0; i < arguments.length; i += 1) {
            if (arguments[i] === '') {
                continue;
            }
            if (url.length > 0 && url[url.length-1] !== '/') {
                url = url + '/' + arguments[i];
            } else {
                url = url + arguments[i];
            }
        }
        url = url.replace(/\/\/+/, '/');
        return url;
    };
    
    var parse = function (url) {
        // an `a` element with an href allows attr-access to the parsed segments of a URL
        // a = parse_url("http://localhost:8888/path/name#hash")
        // a.protocol = "http:"
        // a.host     = "localhost:8888"
        // a.hostname = "localhost"
        // a.port     = 8888
        // a.pathname = "/path/name"
        // a.hash     = "#hash"
        var a = document.createElement("a");
        a.href = url;
        return a;
    };
    
    var encode_uri_components = function (uri) {
        // encode just the components of a multi-segment uri,
        // leaving '/' separators
        return uri.split('/').map(encodeURIComponent).join('/');
    };
    
    return {
        path_join : path_join,
        encode_uri_components : encode_uri_components,
        parse : parse
    };
    
}); 
