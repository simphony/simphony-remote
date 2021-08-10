<template>
  <div class="form-group">
    <label>Startup file</label><br>
    <input v-model="srdata">
  </div>
</template>

<script>
  let Vue = require('vue');

  module.exports = Vue.component('srdata-component', {
    props: ['configDict'],

    data: function () {
      return {
        srdata: this.configDict.srdata
      };
    },

    watch: {
      configDict: function () { this.srdata = this.configDict.srdata; },
      srdata: function () { this.$emit('update:configDict', { srdata: this.srdata }); }
    }
  });

</script>
