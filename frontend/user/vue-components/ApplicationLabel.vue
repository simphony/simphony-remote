<template>
  <ul v-if="currentApp !== null" class="nav navbar-nav">
    <li class="dropdown notifications-menu">
      <a href="#" class="dropdown-toggle cust-padding" data-toggle="dropdown" aria-expanded="false">
        <img class="app-icon"
        :src="currentApp.appData.image.icon_128 | iconSrc">

        <span>{{ currentApp.appData.image | appName }}</span>
      </a>

      <ul class="dropdown-menu">
        <li>
          <ul class="menu">

            <!-- Quit button -->
            <li>
              <a href="#"
              id="quit-button"
              :class="{ 'disabled-entry': !currentApp.isRunning() }"
              @click="stopApplication()">
                <i class="fa fa-times text-danger"></i>
                Quit
              </a>
            </li>

            <!-- Share button -->
            <li>
              <a href="#"
              id="share-button"
              :class="{ 'disabled-entry': !(currentApp.isRunning() && clipboardSupported) }"
              :data-clipboard-text="sharedUrl">
                <i class="fa fa-clipboard text-light-blue"></i>
                Share session
              </a>
            </li>

            <!-- Put other settings here -->
          </ul>
        </li>
      </ul>
    </li>
  </ul>
</template>

<script>
  let $ = require("jquery");
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
        if(!this.currentApp.isRunning()) {return new $.Deferred().resolve();}

        let stoppingAppName = this.$options.filters.appName(
          this.currentApp.appData.image);
        return this.model.stopApplication(this.model.selectedIndex).fail((error) => {
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

  .disabled-entry {
    pointer-events: none;
    opacity: 0.4;
  }

  .app-icon {
    width: 32px;
    height: 32px;
    border-radius: 20%;
    border: 1px solid #d2d6de;
  }
</style>
