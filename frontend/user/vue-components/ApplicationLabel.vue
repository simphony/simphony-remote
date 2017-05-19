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
        <li
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

  module.exports = Vue.extend({
    computed: {
      currentApp: function() {
        return this.model.appList[this.model.selectedIndex] || null;
      }
    },

    methods: {
      stopApplication: function(index) {
        // TODO: Handle error
        this.model.stopApplication(this.model.selectedIndex);
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
