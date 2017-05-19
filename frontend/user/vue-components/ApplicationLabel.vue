<template>
  <div v-if="currentApp !== null" class="container">
    <img class="app-icon"
    :src="currentApp.appData.image.icon_128 | iconSrc">

    <button class="stop-button"
    v-if="currentApp.isRunning()"
    @click="stopApplication()"
    :disabled="currentApp.isStopping()">
      <i class="fa fa-times"></i>
    </button>
    <span>{{ currentApp.appData.image | appName }}</span>
  </div>
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
  .container {
    margin: 9px;
  }

  .app-icon {
    position: relative;
    width: 32px;
    height: 32px;
    border-radius: 20%;
    border: 1px solid #d2d6de;
    margin-right: 10px;
  }

  .stop-button {
    position: absolute;
    top: 9px;
    left: 24px;
    z-index: 100;
    width: 32px;
    height: 32px;
    border: 1px solid rgba(0, 0, 0, 0.8);
    background-color: rgba(0, 0, 0, 0.7);
    border-radius: 20%;
    font-size: 18px;
    color: rgba(255, 255, 255, 0.7);
  }
</style>
