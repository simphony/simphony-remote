/*globals: require, console*/
require([
    "jquery",
    "urlutils",
    "dialogs",
    "analytics",
    "home/models",
    "home/views/application_list_view",
    "home/views/application_view",
    "jsapi/v1/resources",
    "handlebars",
    'utils',
    'home/configurables',
], function(
    $,
    urlutils,
    dialogs,
    analytics,
    models,
    application_list_view,
    application_view,
    resources,
    hb,
    utils,
    configurables) {
    "use strict";

    var ga = analytics.init();

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
            .done(function (ids) {
                // We neutralize the potential error from a jXHR request
                // and make sure that all our requests "succeed" so that
                // all/when can guarantee everything is done.

                // These will go out of scope but they are still alive
                // and performing to completion
                var requests = [];
                for (var i = 0; i < ids.length; i++) {
                    requests.push($.Deferred());
                }

                // We need to bind with the current i index in the loop
                // Hence we create these closures to grab the index for
                // each new index
                var done_callback = function(index) {
                    return function(rep) {
                        requests[index].resolve(rep);
                    };
                };
                var fail_callback = function(index) {
                    return function() {
                        requests[index].resolve(null);
                    };
                };

                for (i = 0; i < ids.length; i++) {
                    var id = ids[i];
                    resources.Application.retrieve(id)
                        .done(done_callback(i))
                        .fail(fail_callback(i));

                }

                utils.all(requests)
                    .done(function (promises) {
                        // Fills the local application model with the results of the
                        // retrieve promises.
                        var data = [];
                        for (var i = 0; i < promises.length; i++) {
                            var result = promises[i];
                            if (result !== null) {
                                data.push(result);
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

    var Status = {
        RUNNING: "RUNNING",
        STARTING: "STARTING",
        STOPPING: "STOPPING",
        STOPPED: "STOPPED"
    };

    // Ember objects:

    var AppList = Ember.Application.create({
        LOG_TRANSITIONS: true, // For debug
        rootElement: '#applist'
    });

    AppList.IconSrcHelper = Ember.Helper.helper(function([app_data]){
        var icon_data = app_data.image.icon_128;
        return (
            icon_data ?
            "data:image/png;base64,"+icon_data :
            urlutils.path_join(
                this.base_url, "static", "images", "generic_appicon_128.png"
            )
        );
    });

    AppList.AppNameHelper = Ember.Helper.helper(function([app_data]){
        return (
            app_data.image.ui_name ?
            app_data.image.ui_name :
            app_data.image.name
        );
    });

    AppList.ApplicationListComponent = Ember.Component.extend({
        init: function() {
            this._super(...arguments);

            this.set('list_loading', true);
            this.set('empty_list', false);

            this.set('app_data', null);
            this.set('configurables', []);
            this.set('status', []);

            this.set('application_entry_list', []);

            this.fill_list();
        },

        fill_list: function() {
            return $.when(
                available_applications_info()
            ).done(function (app_data) {
                this.set('app_data', app_data);

                var num_entries = app_data.length;

                if(num_entries == 0) {
                    this.set('empty_list', true);
                } else {
                    // Add the options for some image types
                    for (var i = 0; i < num_entries; ++i) {
                        this._update_application(i);
                    }
                }

                this.set('list_loading', false);
            }.bind(this));
        },

        _update_application: function(index) {
            // Updates the configurables submodel for a given application index.
            var app_data = this.get('app_data')[index];
            var image = app_data.image;

            this.get('configurables')[index] = {};

            for (var i = 0; i < image.configurables.length; ++i) {
                var tag = image.configurables[i];

                // If this returns null, the tag has not been recognized
                // by the client. skip it and let the server deal with the
                // missing data, either by using a default or throwing
                // an error.
                var ConfigurableCls = configurables.from_tag(tag);

                if (ConfigurableCls !== null) {
                    this.get('configurables')[index][tag] = new ConfigurableCls();
                }
            }

            var app_status = app_data.container === null ?
                Status.STOPPED :
                Status.RUNNING;
            this.get('status')[index] = app_status;

            var application_entry_list = this.get('application_entry_list');
            this.set('application_entry_list', application_entry_list.concat([{
                index: index,
                app_data: app_data,
                app_status: app_status.toLowerCase()
            }]));
        }
    });
});
