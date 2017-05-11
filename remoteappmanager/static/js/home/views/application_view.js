define([
    "urlutils",
    "utils",
    '../../components/vue/dist/vue'
], function (urlUtils, utils, Vue) {
    "use strict";

    var ApplicationView = Vue.extend({
        template:
            '<!-- Application View -->' +
            '<section id="appview"' +
            '         v-if="currentApp !== null"' +
            '         :class="{ content: true, \'no-padding\': currentApp.isRunning() }">' +
            '  <!-- Start Form -->' +
            '  <transition name="fade" v-if="!currentApp.isRunning()">' +
            '  <div v-if="currentApp.isStopped()" class="row">' +
            '    <div class="col-md-offset-2 col-md-8">' +
            '      <div class="box box-primary">' +
            '        <div class="box-header with-border">' +
            '          <h3 class="box-title">{{ currentApp.appData.image | appName }}</h3>' +
            '          <div class="box-tools pull-right"></div>' +
            '        </div>' +
            '        <div class="box-body">' +
            '          <h4>Description</h4>' +
            '          <span>{{ currentApp.appData.image.description }}</span>' +

            '          <h4>Policy</h4>' +

            '          <ul class="policy">' +
            '            <!-- Workspace -->' +
            '            <li v-if="appPolicy.allow_home">' +
            '                Workspace accessible' +
            '            </li>' +
            '            <li v-else>' +
            '                Workspace not accessible' +
            '            </li>' +

            '            <!-- Volume mounted -->' +
            '            <li v-if="appPolicy.volume_source && appPolicy.volume_target && appPolicy.volume_mode">' +
            '              Volume mounted: {{ appPolicy.volume_source }} &#x2192; {{ appPolicy.volume_target }} ({{ appPolicy.volume_mode }})' +
            '            </li>' +
            '            <li v-else>' +
            '              No volumes mounted' +
            '            </li>' +
            '          </ul>' +

            '          <h4>Configuration</h4>' +
            '          <form class="configuration">' +
            '            <fieldset v-if="currentApp.configurables.length === 0">No configurable options for this image</fieldset>' +
            '            <fieldset v-else :disabled="currentApp.isStarting()">' +
            '              <component v-for="configurable in currentApp.configurables"' +
            '                         :key="configurable.tag"' +
            '                         :is="configurable.tag + \'-component\'"' +
            '                         :config_dict.sync="configurable.config_dict"></component>' +
            '            </fieldset>' +
            '          </form>' +
            '        </div>' +

            '        <!-- Start Button -->' +
            '        <div class="box-footer">' +
            '          <button class="btn btn-primary pull-right start-button"' +
            '                  @click="startApplication()"' +
            '                  :disabled="currentApp.isStarting()">' +
            '            Start' +
            '          </button>' +
            '        </div>' +
            '      </div>' +
            '    </div>' +
            '  </div>' +
            '  </transition>' +

            '  <!-- Application View -->' +
            '  <iframe v-if="currentApp.isRunning()"' +
            '          id="application"' +
            '          frameBorder="0"' +
            '          :src="appSource"' +
            '          :style="{ minWidth: getIframeSize()[0] + \'px\', minHeight: getIframeSize()[1] + \'px\' }">' +
            '  </iframe>' +
            '</section>',

        computed: {
            currentApp: function() {
                return this.model.appList[this.model.selectedIndex] || null;
            },
            appPolicy: function() {
                return this.currentApp.appData.image.policy;
            },
            appSource: function() {
                var url = urlUtils.path_join(
                    window.apidata.base_url,
                    'containers',
                    this.currentApp.appData.container.url_id
                );
                var output = this.currentApp.delayed ? url : url + '/';

                this.currentApp.delayed = false;

                return output;
            }
        },

        methods: {
            startApplication: function() {
                this.$emit('startApplication', this.currentApp);
                this.model.startApplication();
            },
            getIframeSize: function() {
                return utils.max_iframe_size();
            },
            focusIframe: function() {
                var iframe = this.$el.querySelector('iframe');
                if(iframe !== null) {
                    iframe.focus();
                }
            }
        },

        updated: function() { this.focusIframe(); }
    });

    return {
        ApplicationView : ApplicationView
    };
});
