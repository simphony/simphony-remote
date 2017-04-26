define([
    "urlutils",
    "utils",
    "gamodule",
    "dialogs",
    "home/models",
    '../../components/vue/dist/vue.min',
    "jsapi/v1/resources"
], function (urlutils, utils, gamodule, dialogs, models, Vue, resources) {
    "use strict";

    var ga = gamodule.init();
    var Status = utils.Status;

    var ApplicationView = Vue.extend({
        el: 'section.content',

        data: function() {
            return {
                model: { app_list: [], selected_index: null }
            };
        },

        computed: {
            current_app: function() {
                return this.model.app_list[this.model.selected_index] || null;
            },
            app_policy: function() {
                return this.current_app.app_data.image.policy;
            },
            app_source: function() {
                return urlutils.path_join(
                    window.apidata.base_url,
                    'containers',
                    this.current_app.app_data.container.url_id
                );
            },
            iframe_size: function() {
                return utils.max_iframe_size();
            }
        },

        methods: {
            start_application: function() {
                var selected_index = this.model.selected_index;
                var current_app = this.current_app;

                current_app.status = Status.STARTING;

                var configurables_data = {};
                current_app.configurables.forEach(function(configurable) {
                    var tag = configurable.tag;
                    configurables_data[tag] = configurable.as_config_dict();
                });

                resources.Container.create({
                    mapping_id: current_app.app_data.mapping_id,
                    configurables: configurables_data
                }).done(function() {
                    ga("send", "event", {
                        eventCategory: "Application",
                        eventAction: "start",
                        eventLabel: current_app.app_data.image.name
                    });

                    this.model.update_idx(selected_index)
                        .fail(function(error) {
                            current_app.status = Status.STOPPED;
                            dialogs.webapi_error_dialog(error);
                        });
                }.bind(this)).fail(function(error) {
                    current_app.status = Status.STOPPED;
                    dialogs.webapi_error_dialog(error);
                });
            }
        },

        filters: utils.filters
    });

    return {
        ApplicationView : ApplicationView
    };
});
