// This module contains the setup for google analytics.
// MUST not be renamed to analytics. Some blockers rely on name
// matching to prevent loading.
define([
    "components/vue/dist/vue.min"
], function (Vue) {
    "use strict";

    function init() {
        var module;

        if (window.apidata.analytics !== undefined) {
            window.ga('create', window.apidata.analytics.tracking_id, 'auto');
        } else {
            window.ga = function () {
            };
        }
        module = function () {
            window.ga.apply(this, arguments);
        };
        return module;
    }

    var GaView = Vue.extend({
        beforeCreate: function() {
            this.ga = init();
        },

        computed: {
            current_app: function() {
                return this.model.app_list[this.model.selected_index] || null;
            }
        },

        watch: {
            'current_app.status': function() {
                if(this.current_app.is_starting()) {
                    this.ga("send", "event", {
                        eventCategory: "Application",
                        eventAction: "start",
                        eventLabel: this.current_app.app_data.image.name
                    });
                }
            }
        }
    });

    return {
        init: init, // For testing purpose
        GaView: GaView
    };
});
