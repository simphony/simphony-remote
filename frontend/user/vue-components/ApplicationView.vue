<template>
  <!-- Application View -->
  <section id="appview"
  v-if="currentApp !== null"
  :class="{ content: true, 'no-padding': currentApp.isRunning() }">
    <!-- Start Form -->
    <div v-if="!currentApp.isRunning()" class="row">
      <div class="col-md-offset-2 col-md-8">
        <div class="box box-standard">
          <div class="box-header with-border">
            <h3 class="box-title">{{ currentApp.appData.image | appName }}</h3>
          </div>
          <div class="box-body">
            <img class="pull-right app-logo" :src="currentApp.appData.image.icon_128 | iconSrc"></img>
            <h4>Type</h4>
            <span>{{ currentApp.appData.image.type == "webapp" ? "Web": "VNC" }} application</span>

            <h4>Description</h4>
            <span id="app-description">{{ currentApp.appData.image.description }}</span>

            <h4>Policy</h4>

            <ul class="policy">
              <!-- Workspace -->
              <li v-if="appPolicy.allow_home">
                Workspace accessible
              </li>
              <li v-else>
                Workspace not accessible
              </li>

              <!-- Volume mounted -->
              <li v-if="appPolicy.volume_source && appPolicy.volume_target && appPolicy.volume_mode">
                Volume mounted: {{ appPolicy.volume_source }} &#x2192; {{ appPolicy.volume_target }} ({{ appPolicy.volume_mode }})
              </li>
              <li v-else>
                No volumes mounted
              </li>
            </ul>

            <h4>Configuration</h4>
            <form class="configuration">
              <fieldset v-if="currentApp.configurables.length === 0">No configurable options for this image</fieldset>
              <fieldset v-else :disabled="!currentApp.isStopped()">
                <fieldset v-if="appPolicy.allow_startup_data">
                  <component v-for="configurable in currentApp.configurables"
                  :key="configurable.tag"
                  :is="configurable.tag + '-component'"
                  :configDict.sync="configurable.configDict"></component>
                </fieldset>
                <fieldset v-else>
                  <component v-for="configurable in currentApp.configurables" v-if="configurable.tag !== 'startupdata'"
                  :key="configurable.tag"
                  :is="configurable.tag + '-component'"
                  :configDict.sync="configurable.configDict"></component>
                </fieldset>
              </fieldset>
            </form>
          </div>

          <!-- Start Button -->
          <div class="box-footer">
            <button id="start-button" class="btn btn-primary pull-right start-button"
            @click="startApplication()"
            :disabled="!currentApp.isStopped()"> Start </button>
          </div>

          <!-- Loading spinner -->
          <div class="overlay" v-show="!currentApp.isStopped()">
            <i class="fa fa-refresh fa-spin"></i>
          </div>
        </div>
      </div>
    </div>

    <!-- Application View -->
    <iframe v-if="currentApp.isRunning()"
    id="application"
    frameBorder="0"
    :src="appSource"
    :style="{ minWidth: getIframeSize()[0] + 'px', minHeight: getIframeSize()[1] + 'px' }">
    </iframe>
  </section>
</template>

<script>
  let $ = require("jquery");
  let Vue = require("vue");
  let urlUtils = require("urlutils");
  let utils = require("utils");
  require("toolkit");

  module.exports = Vue.extend({
    computed: {
      currentApp: function() {
        return this.model.appList[this.model.selectedIndex] || null;
      },
      appPolicy: function() {
        return this.currentApp.appData.image.policy;
      },
      appSource: function() {
        let url = urlUtils.appUrl(this.currentApp);

        let output = this.currentApp.delayed ? url : url + '/';
        this.currentApp.delayed = false;

        return output;
      }
    },

    methods: {
      startApplication: function() {
        if(!this.currentApp.isStopped()) {return new $.Deferred().resolve();}

        let startingApp = this.currentApp;
        let startingAppName = this.$options.filters.appName(startingApp.appData.image);
        return this.model.startApplication(this.model.selectedIndex)
        .done(() => {
          this.$emit('startApplication', startingApp);
        })
        .fail((error) => {
          this.$emit('error', {
            title: 'Error when starting ' + startingAppName,
            code: error.code,
            message: error.message
          });
        });
      },
      getIframeSize: function() {
        return utils.maxIframeSize();
      },
      focusIframe: function() {
        // In case $el is not rendered, it's an empty comment '<!---->'
        if(this.$el.nodeType === Node.ELEMENT_NODE &&
           this.$el.querySelector('iframe') !== null) {
          this.$el.querySelector('iframe').focus();
        }
      }
    },

    updated: function() { this.focusIframe(); }
  });
</script>

<style scoped>
  .no-padding {
    padding: 0px;
  }

  .app-logo {
    border-radius: 20%;
  }

  #application {
    width: 100%;
    height: 100%;
  }
</style>
