<template>
  <div class="form-group">
    <label>Startup file</label><br>
    <input v-model="startupdata">
  </div>
</template>

<script>
  let Vue = require('vue');

  module.exports = Vue.component('startupdata-component', {
    props: ['configDict'],

    data: function () {
      return {
        startupdata: this.configDict.startupdata
      };
    },

    watch: {
      configDict: function () { this.startupdata = this.configDict.startupdata; },
      startupdata: function () { this.$emit('update:configDict', { startupdata: this.startupdata }); }
    }
  });

</script>
