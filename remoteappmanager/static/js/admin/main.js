/*globals: require, console*/
require([
  "components/vue/dist/vue.min",
  "components/vue-router/dist/vue-router.min",
], function(Vue, VueRouter) {
  "use strict";

  // install router
  Vue.use(VueRouter);
  
  var Foo = { template: '<div>hello</div>' };
  
  var router = new VueRouter({
    routes: [
      { path: '/*', component: Foo }
    ]
  });

  const app = new Vue({
    router
  }).$mount('#app');

});
