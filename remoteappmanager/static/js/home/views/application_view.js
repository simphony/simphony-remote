define([
    'jquery',
    "urlutils",
    "utils",
    '../../components/vue/dist/vue.min'
], function ($, urlutils, utils, Vue) {
    "use strict";

    var ApplicationView = Vue.extend({
        computed: {
            current_app: function() {
                return this.model.app_list[this.model.selected_index] || null;
            },
            app_policy: function() {
                return this.current_app.app_data.image.policy;
            },
            app_source: function() {
                var url = urlutils.path_join(
                    window.apidata.base_url,
                    'containers',
                    this.current_app.app_data.container.url_id
                );
                var output = this.current_app.delayed ? url : url + '/';

                this.current_app.delayed = false;

                return output;
            }
        },

        methods: {
            start_application: function() {
                this.$emit('start_application', this.current_app);
                this.model.start_application();
            },
            get_iframe_size: function() {
                return utils.max_iframe_size();
            }
        },

        updated: function() { $('iframe').focus(); }
    });

    return {
        ApplicationView : ApplicationView
    };
});
