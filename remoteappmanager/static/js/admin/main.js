/*globals: require, console*/
require([
  "vue/dist/vue.min",
  "vue-router/dist/vue-router.min",
  "vue-components/main_view"
], function(Vue, Router, App, MainView) {
  "use strict";

  // install router
  Vue.use(Router);

  var router = new Router();

  router.map({
    '/user/:username': {
      component: MainView
    }
  });

  router.beforeEach(function () {
    window.scrollTo(0, 0);
  });

  router.start(App, '#adminapp');
    
});
