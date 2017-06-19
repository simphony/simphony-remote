<template>
  <ul v-if="currentApp !== null" class="nav navbar-nav">
    <li id="application-settings" class="dropdown notifications-menu">
      <a href="#" class="dropdown-toggle cust-padding" data-toggle="dropdown" aria-expanded="false">
        <img class="app-icon"
        :src="currentApp.appData.image.icon_128 | iconSrc">

        <span>{{ currentApp.appData.image | appName }}</span>
      </a>

      <ul class="dropdown-menu">
        <li>
          <ul class="menu">

            <!-- Share button -->
            <li>
              <a href="#"
              id="share-button"
              :class="{ 'disabled-entry': !currentApp.isRunning() || currentApp.appData.image.type == 'webapp' }"
              @click="shareDialog.visible = true">
                <i class="fa fa-clipboard text-light-blue"></i>
                Share session
              </a>
            </li>

            <!-- Quit button -->
            <li>
              <a href="#"
              id="quit-button"
              :class="{ 'disabled-entry': !currentApp.isRunning() }"
              @click="quitDialog.visible = true">
                <i class="fa fa-times text-danger"></i>
                Quit
              </a>
            </li>

            <!-- Put other settings here -->
          </ul>
        </li>
      </ul>

      <!-- Modal dialog for the share button -->
      <modal-dialog v-if="shareDialog.visible">
        <div class="modal-header"><h4>Share Session</h4></div>
        <div class="modal-body">
          <div class="input-group">
            <input id="shared-url" type="text" class="form-control" :value="sharedUrl + '/'"></input>
            <span class="input-group-btn">
              <button id="cp-clipboard-button" class="btn btn-primary" data-clipboard-target="#shared-url" data-toggle="tooltip" title="Copy to clipboard">
                <i class="fa fa-clipboard"></i>
              </button>
            </span>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-default" @click="shareDialog.visible = false">Close</button>
        </div>
      </modal-dialog>

      <!-- Modal dialog for the quit button -->
      <confirm-dialog
      v-if="quitDialog.visible"
      :okCallback="() => {quitDialog.visible = false; stopApplication();}"
      :closeCallback="() => {quitDialog.visible = false;}">
          <div>Are you sure you want to quit <b>{{ currentApp.appData.image | appName }}</b> ? (irreversible)</div>
      </confirm-dialog>
    </li>
  </ul>
</template>

<script>
  let $ = require("jquery");
  let Vue = require("vue");
  let Clipboard = require('clipboard');
  let URL = require('url-parse');
  let urlUtils = require('urlutils');
  require('toolkit');

  module.exports = Vue.extend({
    data: function() {
      return { shareDialog: {visible: false}, quitDialog: {visible: false} };
    },

    mounted: function() {
      new Clipboard('#cp-clipboard-button');
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
