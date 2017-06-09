var Vue = require("vue");

var getRenderedText = function(Component, propsData) {
  var Ctor = Vue.extend(Component);
  var vm = new Ctor({ propsData: propsData }).$mount();
  return vm.$el.textContent;
};

module.exports = {
  getRenderedText
};
