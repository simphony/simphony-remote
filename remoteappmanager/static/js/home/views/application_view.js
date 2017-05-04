define([
    'jquery',
    "urlutils",
    "utils",
    '../../components/vue/dist/vue.min'
], function ($, urlutils, utils, Vue) {
    "use strict";

    var ApplicationView = Vue.extend({
        template:
            '<!-- Application View -->' +
            '<section id="appview"' +
            '         v-if="current_app !== null"' +
            '         :class="{ content: true, \'no-padding\': current_app.is_running() }">' +
            '  <!-- Start Form -->' +
            '  <div v-if="!current_app.is_running()" class="row">' +
            '    <div class="col-md-offset-2 col-md-8">' +
            '      <div class="box box-primary">' +
            '        <div class="box-header with-border">' +
            '          <h3 class="box-title">{{ current_app.app_data.image | app_name }}</h3>' +
            '          <div class="box-tools pull-right"></div>' +
            '        </div>' +
            '        <div class="box-body">' +
            '          <h4>Policy</h4>' +

            '          <ul class="policy">' +
            '            <!-- Workspace -->' +
            '            <li v-if="app_policy.allow_home">' +
            '                Workspace accessible' +
            '            </li>' +
            '            <li v-else>' +
            '                Workspace not accessible' +
            '            </li>' +

            '            <!-- Volume mounted -->' +
            '            <li v-if="app_policy.volume_source && app_policy.volume_target && app_policy.volume_mode">' +
            '              Volume mounted: {{ app_policy.volume_source }} &#x2192; {{ app_policy.volume_target }} ({{ app_policy.volume_mode }})' +
            '            </li>' +
            '            <li v-else>' +
            '              No volumes mounted' +
            '            </li>' +
            '          </ul>' +

            '          <h4>Configuration</h4>' +
            '          <form class="configuration">' +
            '            <fieldset v-if="current_app.configurables.length === 0">No configurable options for this image</fieldset>' +
            '            <fieldset v-else>' +
            //'              <component v-for="configurable in current_app.configurables" :is="configurable.tag"></component>' +
            '            </fieldset>' +
            '          </form>' +
            '        </div>' +

            '        <!-- Start Button -->' +
            '        <div class="box-footer">' +
            '          <button class="btn btn-primary pull-right start-button"' +
            '                  @click="start_application()"' +
            '                  :disabled="current_app.is_starting()">' +
            '            Start' +
            '          </button>' +
            '        </div>' +
            '      </div>' +
            '    </div>' +
            '  </div>' +

            '  <!-- Application View -->' +
            '  <iframe v-if="current_app.is_running()"' +
            '          id="application"' +
            '          frameBorder="0"' +
            '          :src="app_source"' +
            '          :style="{ minWidth: get_iframe_size()[0] + \'px\', minHeight: get_iframe_size()[1] + \'px\' }">' +
            '  </iframe>' +
            '</section>',

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
