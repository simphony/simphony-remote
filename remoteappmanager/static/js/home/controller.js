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
    "init",
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
    init,
    utils,
    configurables) {
    "use strict";

    var ga = analytics.init();
    init.handlebars();

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

    AppList.ApplicationListComponent = Ember.Component.extend({
        init: function() {
            this._super(...arguments);

            this.set('list_loading', true);
            this.set('empty_list', false);

            this.set('app_data', null);
            this.set('configurables', []);
            this.set('status', [])

            this.fill_list();
        },

        fill_list: function() {
            return $.when(
                available_applications_info()
            ).done(function (app_data) {
                this.set('app_data', app_data);

                var num_entries = this.get('app_data').length;

                if(num_entries == 0) {
                    this.set('empty_list', true);
                } else {
                    // Add the options for some image types
                    for (var i = 0; i < num_entries; ++i) {
                        this._update_image(i);
                    }
                }

                this.set('list_loading', false);
            }.bind(this));
        },

        _update_image: function(index) {
            // Updates the configurables submodel for a given application index.
            var image = this.get('app_data')[index].image;
            var app_data = this.get('app_data')[index];

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

            if (app_data.container === null) {
                this.get('status')[index] = Status.STOPPED;
            } else {
                this.get('status')[index] = Status.RUNNING;
            }
        }
    });

    // This model keeps the retrieved content from the REST query locally.
    // It is only synchronized at initial load.
    /*var model = new models.ApplicationListModel();
    var app_list_view = new application_list_view.ApplicationListView(model);
    var app_view = new application_view.ApplicationView(model);

    app_list_view.entry_clicked = function (index) {
        model.selected_index = index;
        app_list_view.update_selected();
        app_view.render(false, 200);
    };

    app_list_view.stop_button_clicked = function(index) {
        if (model.status[index] === models.Status.STOPPING) {
            return;
        }
        model.status[index] = models.Status.STOPPING;

        var app_info = model.app_data[index];
        var url_id = app_info.container.url_id;

        app_list_view.update_entry(index);

        resources.Container.delete(url_id)
            .done(function () {
                model.update_idx(index)
                    .done(function() {
                        app_list_view.update_entry(index);
                        app_view.render(true);
                    })
                    .fail(function(error) {
                        model.status[index] = models.Status.STOPPED;
                        app_list_view.update_entry(index);
                        app_view.render(true);
                        dialogs.webapi_error_dialog(error);
                    });
                })
            .fail(
                function (error) {
                    model.status[index] = models.Status.STOPPED;
                    app_list_view.update_entry(index);
                    app_view.render(true);
                    dialogs.webapi_error_dialog(error);
                });
    };

    app_view.start_button_clicked = function (index) {
        // The container is not running. This is a start button.
        var mapping_id = model.app_data[index].mapping_id;
        var image_name = model.app_data[index].image.name;

        if (model.status[index] === models.Status.STARTING) {
            return;
        }

        model.status[index] = models.Status.STARTING;
        app_view.render(false, null);
        app_list_view.update_entry(index);

        var configurables_data = {};
        var configurables = model.configurables[index];
        configurables_data = {};

        Object.getOwnPropertyNames(configurables).forEach(
            function(val, idx, array) {   // jshint ignore:line
                var configurable = configurables[val];
                var tag = configurable.tag;
                configurables_data[tag] = configurable.as_config_dict();
            }
        );

        resources.Container.create({
            mapping_id: mapping_id,
            configurables: configurables_data
        }).done(function() {
            ga("send", "event", {
                eventCategory: "Application",
                eventAction: "start",
                eventLabel: image_name
            });

            model.update_idx(index)
                .always(function() {
                    app_list_view.update_entry(index);
                    app_list_view.update_selected();
                    app_view.render(true, 200);
                })
                .fail(function(error) {
                    model.status[index] = models.Status.STOPPED;
                    app_list_view.update_entry(index);
                    app_view.render(true, 200);
                    dialogs.webapi_error_dialog(error);
                });
        }).fail(function(error) {
            model.status[index] = models.Status.STOPPED;
            app_list_view.update_entry(index);
            app_list_view.update_selected();
            app_view.render(true, 200);
            dialogs.webapi_error_dialog(error);
        });
    };

    $.when(model.update()).done(function () {
        app_list_view.render();
        app_view.render(false, 200);
    });*/

});
