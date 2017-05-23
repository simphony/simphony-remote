<template>
  <ul v-if="currentApp !== null" class="nav navbar-nav">
    <!-- Error dialog -->
    <confirm-dialog v-if="stoppingError.show"
    :title="'Error when stopping ' + stoppingError.appName"
    :okCallback="closeDialog">
      <div id="error-msg" class="alert alert-danger">
        <strong>Code: {{stoppingError.code}}</strong>
        <span>{{stoppingError.message}}</span>
      </div>
    </confirm-dialog>

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
        <li
        id="stop-button"
        :class="{ disabled: !currentApp.isRunning() }"
        @click="stopApplication()">
          <a href="#">
            <i class="fa fa-times text-danger"></i>
            Stop Application
          </a>
          <!-- Put other settings here -->
        </li>
      </ul>
    </li>
  </ul>
</template>

<script>
  let Vue = require("vuejs");
  require('toolkit');

  module.exports = Vue.extend({
    data: function() {
      return {
        stoppingError: { show: false, appName: '', code: '', message: '' }
      };
    },

    computed: {
      currentApp: function() {
        return this.model.appList[this.model.selectedIndex] || null;
      }
    },

    methods: {
      stopApplication: function() {
        let stoppingAppName = this.$options.filters.appName(
          this.currentApp.appData.image);
        this.model.stopApplication(this.model.selectedIndex).fail((error) => {
          this.stoppingError.code = error.code;
          this.stoppingError.message = error.message;
          this.stoppingError.appName = stoppingAppName;
          this.stoppingError.show = true;
        });
      },
      closeDialog: function() {
        this.stoppingError.show = false;
      },
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
