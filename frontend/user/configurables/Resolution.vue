<template>
  <div class="form-group">
    <label>Resolution</label>
    <select class="form-control" v-model="resolution">
      <option v-for="resolutionOption in resolutionOptions">
        {{resolutionOption}}
      </option>
    </select>
  </div>
</template>

<script>
  let Vue = require('vuejs');

  // Your component tag must have '-component' suffix
  module.exports = Vue.component('resolution-component', {
    // Your configurable must have a "configDict" property from the model
    props: ['configDict'],

    data: function() {
      return {
        resolution: this.configDict.resolution,
        resolutionOptions: ['Window', '1920x1080', '1280x1024', '1280x800', '1024x768']
      };
    },

    watch: {
      configDict: function() { this.resolution = this.configDict.resolution; }, // model -> view update
      resolution: function() { this.$emit('update:configDict', { resolution: this.resolution }); } // view -> model update
    }
  });
</script>
