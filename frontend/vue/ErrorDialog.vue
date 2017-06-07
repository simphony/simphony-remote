<template>
  <confirm-dialog v-if="errorList.length"
  :title="errorList[0].title || 'Error'"
  :okCallback="okCallback"
  :closeCallback="closeCallback">
    <div class="alert alert-danger">
      <strong v-if="errorList[0].code !== undefined">Code: {{errorList[0].code}}</strong>
      <span>{{errorList[0].message || 'unknown error'}}</span>
    </div>
  </confirm-dialog>
</template>

<script>
  let Vue = require("vue");
  require("toolkit");

  module.exports = Vue.extend({
    data: function() {
      return { errorList: [] };
    },

    methods: {
      okCallback: function() {
        // Display next error
        this.errorList.shift();
      },
      closeCallback: function() {
        // Close dialog by emptying the errorList
        this.errorList.splice(0, this.errorList.length);
      }
    }
  });
</script>
