/*globals: require, console*/
require([
  "components/vue/dist/vue.min",
  "components/vue-router/dist/vue-router.min",
], function(Vue, VueRouter) {
  "use strict";

  // install router
  Vue.use(VueRouter);
  var MainView = {
    template: "hello"
  };

  var router = new VueRouter({
    routes: [
      {
        path: '/',
        component: MainView
      }
    ]
  });

  var app = new Vue({
    router
  }).$mount("#adminapp");
    
});
