define([
  "components/vue/dist/vue"
], function(Vue) {
  "use strict";
  
  var getRenderedText = function(Component, propsData) {
    var Ctor = Vue.extend(Component);
    var vm = new Ctor({ propsData: propsData }).$mount();
    return vm.$el.textContent;
  };
  
  return {
    getRenderedText: getRenderedText
  };
});
