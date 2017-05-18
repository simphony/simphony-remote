var $ = require("jquery");
var urlUtils = require("urlutils");
var utils = require("utils");

var object_to_query_args = function (obj) {
  var keys = Object.keys(obj);
  if (keys.length === 0) {
    return "";
  }

  var result = [];
  for (var idx in keys) {
    var key = keys[idx];
    var value = obj[key];
    var key_enc = encodeURIComponent(key);
    if ($.isArray(value)) {
      for (var v in value) {
        result.push(key_enc+"="+encodeURIComponent(v));
      }
    } else {
      result.push(key_enc+"="+encodeURIComponent(value));
    }
  }

  return result.join("&");
};

var API = (function () {
  // Object representing the interface to the Web API.
  // @param base_url : the url at which to find the web API endpoint.
  var self = {};
  self.base_urlpath = "/user/admin/";
  self.default_options = {
    contentType: "application/json",
    cache: false,
    dataType : null,
    processData: false,
    success: null,
    error: null
  };

  self.request = function (req_type, endpoint, body, query_args) {
    // Performs a request to the final endpoint
    var options = {};
    utils.update(options, self.default_options);
    utils.update(options, {
      type: req_type,
      data: body
    });

    var url = urlUtils.pathJoin(
        self.base_urlpath,
        "api", "v1",
        urlUtils.encodeUriComponents(endpoint)
      )+'/';

    if (query_args) {
      url = url + "?" + object_to_query_args(query_args);
    }
    return $.ajax(url, options);
  };
  return self;
})();

var RestError = function(code, message) {
  console.log("Creating error "+code+" message: "+message);
  this.code = code;
  this.message = message;
};

var fail_handler = function(promise, jqXHR) {
  var status = jqXHR.status;
  var payload = null;
  try {
    payload = JSON.parse(jqXHR.responseText);
  } catch (e) {
    // Suppress any syntax error and discard the payload
  }

  var err = new RestError(status, "");
  if (payload !== null) {
    utils.update(err, payload);
  }
  promise.reject(err);
};

var create_handler = function(promise, data, textStatus, jqXHR) {
  var status = jqXHR.status;

  var payload = null;
  try {
    payload = JSON.parse(data);
  } catch (e) {
    // Suppress any syntax error and discard the payload
  }

  if (status !== 201) {
    // Strange situation in which the call succeeded, but
    // not with a 201. Just do our best.
    console.log(
      "Create succeded but response with status " +
      status +
      " instead of 201."
    );
    promise.reject(status, payload);
    return;
  }

  var id, location;
  try {
    location = jqXHR.getResponseHeader('Location');
    var url = urlUtils.parse(location);
    var arr = url.pathname.replace(/\/$/, "").split('/');
    id = arr[arr.length - 1];
  } catch (e) {
    console.log("Response had invalid or absent Location header");
    promise.reject(status, payload);
    return;
  }
  promise.resolve(id, location);
};

var create_singleton_handler = function(promise, data, textStatus, jqXHR) {
  var status = jqXHR.status;

  var payload = null;
  try {
    payload = JSON.parse(data);
  } catch (e) {
    // Suppress any syntax error and discard the payload
  }

  if (status !== 201) {
    // Strange situation in which the call succeeded, but
    // not with a 201. Just do our best.
    console.log(
      "Create succeded but response with status " +
      status +
      " instead of 201."
    );
    promise.reject(status, payload);
    return;
  }

  var location;
  try {
    location = jqXHR.getResponseHeader('Location');
  } catch (e) {
    console.log("Response had invalid or absent Location header");
    promise.reject(status, payload);
    return;
  }
  promise.resolve(location);
};

var update_handler = function(promise, data, textStatus, jqXHR) {
  var status = jqXHR.status;

  var payload = null;
  try {
    payload = JSON.parse(data);
  } catch (e) {
    // Suppress any syntax error and discard the payload
  }

  if (status !== 204) {
    // Strange situation in which the call succeeded, but
    // not with a 201. Just do our best.
    console.log(
      "Update succeded but response with status " +
      status +
      " instead of 204."
    );
    promise.reject(status, payload);
    return;
  }

  promise.resolve();
};

var delete_handler = function(promise, data, textStatus, jqXHR) {
  var status = jqXHR.status;
  var payload = null;
  try {
    payload = JSON.parse(data);
  } catch (e) {
    // Suppress any syntax error and discard the payload
  }

  if (status !== 204) {
    console.log(
      "Delete succeded but response with status " +
      status +
      " instead of 204."
    );
    promise.reject(status, payload);
    return;
  }
  promise.resolve();
};

var retrieve_handler = function(promise, data, textStatus, jqXHR) {
  var status = jqXHR.status;

  var payload = null;
  try {
    payload = JSON.parse(jqXHR.responseText);
  } catch (e) {
    // Suppress any syntax error and discard the payload
  }

  if (status !== 200) {
    console.log(
      "Retrieve succeded but response with status " +
      status +
      " instead of 200."
    );
    promise.reject(status, payload);
    return;
  }

  if (payload === null) {
    console.log(
      "Retrieve succeded but empty or invalid payload"
    );
    promise.reject(status, payload);
    return;
  }

  promise.resolve(payload);
};

var Resource = function(type) {
  this.type = type;

  this.create = function(representation, query_args) {
    var body = JSON.stringify(representation);
    var promise = $.Deferred();

    API.request("POST", type, body, query_args)
      .done(function(data, textStatus, jqXHR) {
        create_handler(promise, data, textStatus, jqXHR);
      })
      .fail(function(jqXHR) {
        fail_handler(promise, jqXHR);
      });

    return promise;
  };

  this.update = function(id, representation, query_args) {
    var body = JSON.stringify(representation);
    var promise = $.Deferred();

    API.request("PUT", urlUtils.pathJoin(type, id), body, query_args)
      .done(function(data, textStatus, jqXHR) {
        update_handler(promise, data, textStatus, jqXHR);
        }
      )
      .fail(function(jqXHR) {
        fail_handler(promise, jqXHR);
      });

    return promise;
  };

  this.delete = function(id, query_args) {
    var promise = $.Deferred();

    API.request("DELETE", urlUtils.pathJoin(type, id), null, query_args)
      .done(function(data, textStatus, jqXHR) {
        delete_handler(promise, data, textStatus, jqXHR);
      }
      )
      .fail(function(jqXHR) {
        fail_handler(promise, jqXHR);
      });

    return promise;
  };

  this.retrieve = function(id, query_args) {
    var promise = $.Deferred();

    API.request("GET", urlUtils.pathJoin(type, id), null, query_args)
      .done(function(data, textStatus, jqXHR) {
        retrieve_handler(promise, data, textStatus, jqXHR);
      }
      )
      .fail(function(jqXHR) {
        fail_handler(promise, jqXHR);
      });

    return promise;
  };

  this.items = function(query_args) {
    var promise = $.Deferred();

    API.request("GET", type, null, query_args)
      .done(function(data, textStatus, jqXHR) {
        var status = jqXHR.status;

        var payload = null;
        try {
          payload = JSON.parse(jqXHR.responseText);
        } catch (e) {
          // Suppress any syntax error and discard the payload
        }

        if (status !== 200) {
          console.log(
            "Items retrieve succeded but response with status " +
            status +
            " instead of 200."
          );
          promise.reject(status, payload);
          return;
        }

        if (payload === null) {
          console.log(
            "Items Retrieve succeded but empty or invalid payload"
          );
          promise.reject(status, payload);
          return;
        }

        promise.resolve(
          payload.identifiers,
          payload.items,
          payload.offset,
          payload.total);
      })
      .fail(function(jqXHR) {
        fail_handler(promise, jqXHR);
      });

    return promise;
  };
};

var SingletonResource = function(type) {
  this.type = type;
  this.create = function(representation, query_args) {
    var body = JSON.stringify(representation);
    var promise = $.Deferred();

    API.request("POST", type, body, query_args)
      .done(function(data, textStatus, jqXHR) {
        create_singleton_handler(promise, data, textStatus, jqXHR);
      })
      .fail(function(jqXHR) {
        fail_handler(promise, jqXHR);
      });

    return promise;
  };
  this.update = function(representation, query_args) {
    var body = JSON.stringify(representation);
    var promise = $.Deferred();

    API.request("PUT", type, body, query_args)
      .done(function(data, textStatus, jqXHR) {
        update_handler(promise, data, textStatus, jqXHR);
      }
      )
      .fail(function(jqXHR) {
        fail_handler(promise, jqXHR);
      });

    return promise;


  };

  this.delete = function(query_args) {
    var promise = $.Deferred();

    API.request("DELETE", type, null, query_args)
      .done(function(data, textStatus, jqXHR) {
        delete_handler(promise, data, textStatus, jqXHR);
      }
      )
      .fail(function(jqXHR) {
        fail_handler(promise, jqXHR);
      });

    return promise;
  };

  this.retrieve = function(query_args) {
    var promise = $.Deferred();

    API.request("GET", type, null, query_args)
      .done(function(data, textStatus, jqXHR) {
        retrieve_handler(promise, data, textStatus, jqXHR);
      }
      )
      .fail(function(jqXHR) {
        fail_handler(promise, jqXHR);
      });

    return promise;
  };
};

module.exports = {
  "Application" : new Resource("applications"),
  "Accounting" : new Resource("accounting"),
  "User" : new Resource("users"),
  "Container" : new Resource("containers"),
  "Stats" : new SingletonResource("stats"),
};