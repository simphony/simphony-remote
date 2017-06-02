<template>
  <ul v-if="currentApp !== null" class="nav navbar-nav">
    <li class="dropdown">
      <a href="#" class="dropdown-toggle cust-padding" data-toggle="dropdown" aria-expanded="false">
        <img class="app-icon"
        :src="currentApp.appData.image.icon_128 | iconSrc">

        <span>{{ currentApp.appData.image | appName }}</span>
      </a>

      <ul class="dropdown-menu" role="menu">
        <li class="disabled">
          <a href="#">Application settings</a>
        </li>
        <li role="separator" class="divider"></li>

        <!-- Stop button -->
        <li
        id="stop-button"
        :class="{ disabled: !currentApp.isRunning() }"
        @click="stopApplication()">
          <a href="#">
            <i class="fa fa-times text-danger"></i>
            Stop Application
          </a>
        </li>

        <!-- Share button -->
        <li
        id="share-button"
        :class="{ disabled: !(currentApp.isRunning() && clipboardSupported) }"
        :data-clipboard-text="sharedUrl">
          <a href="#">
            <i class="fa fa-clipboard text-light-blue"></i>
            Share (copy url to clipboard)
          </a>
        </li>

        <!-- Put other settings here -->
      </ul>
    </li>
  </ul>
</template>

<script>
  let Vue = require("vuejs");
  let Clipboard = require('clipboard');
  let URL = require('url-parse');
  let urlUtils = require('urlutils');
  require('toolkit');

  module.exports = Vue.extend({
    data: function() {
      return { clipboardSupported: Clipboard.isSupported() };
    },

    mounted: function() {
      if(this.clipboardSupported) {
        new Clipboard('#share-button');
      }
    },

    computed: {
      currentApp: function() {
        return this.model.appList[this.model.selectedIndex] || null;
      },
      sharedUrl: function() {
        if(this.currentApp.isRunning()) {
          let url = new URL(window.location.origin);
          url.set('pathname', urlUtils.appUrl(this.currentApp));
          return url.href;
        }
        return "";
      }
    },

    methods: {
      stopApplication: function() {
        let stoppingAppName = this.$options.filters.appName(
          this.currentApp.appData.image);
        this.model.stopApplication(this.model.selectedIndex).fail((error) => {
          this.$emit('error', {
            title: 'Error when stopping ' + stoppingAppName,
            code: error.code,
            message: error.message
          });
        });
      }
    },
  });
</script>

<style scoped>
  .cust-padding {
    padding: 9px;
  }

  .app-icon {
    width: 32px;
    height: 32px;
    border-radius: 20%;
    border: 1px solid #d2d6de;
  }
</style>
