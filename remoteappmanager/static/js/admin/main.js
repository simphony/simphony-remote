/*globals: require, console*/
require([
  "components/vue/dist/vue.min",
  "components/vue-router/dist/vue-router.min",
  "admin/vue-components/MainView",
  "admin/vue-components/ContainersView",
  "admin/vue-components/UsersView",
  "admin/vue-components/ApplicationsView"
], function(
  Vue, 
  VueRouter,
  MainView,
  ContainersView,
  UsersView,
  ApplicationsView) {
  
  "use strict";

  // install router
  Vue.use(VueRouter);
  
  const router = new VueRouter({
    routes: [
      { path: '/', component: MainView },
      { path: '/containers', component: ContainersView },
      { path: '/users', component: UsersView },
      { path: '/applications', component: ApplicationsView }
    ]
  });

  const app = new Vue({
    router
  }).$mount('#app');

});
