<template>
  <div v-if="currentApp !== null">
    <img class="app-icon"
    :src="currentApp.appData.image.icon_128 | iconSrc">

    <button class="stop-button"
    v-if="currentApp.isRunning()"
    @click="stopApplication()"
    :disabled="app.isStopping()">
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
  .app-icon {
    position: relative;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    border-color: black;
    border-width: 1px;
    border-style: solid;
    margin-right: 5px;
    margin-top: -2px;
    background-color: white;
  }

  .stop-button {
    display: none;
    position: absolute;
    top: 10px;
    left: 15px;
    z-index: 100;
    width: 32px;
    height: 32px;
    padding: 0px;
    border: 1px solid rgba(0, 0, 0, 0.8);
    background-color: rgba(0, 0, 0, 0.7);
    border-radius: 50%;
    font-size: 18px;
    color: rgba(255, 255, 255, 0.7);
  }
</style>
