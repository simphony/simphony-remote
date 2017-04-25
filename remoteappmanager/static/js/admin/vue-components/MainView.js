define([
  "components/vue/dist/vue.min"
], function(Vue) {
  "use strict";

  var component = Vue.component("main-view", {
      template: "hello"
    });

  return component;
});
