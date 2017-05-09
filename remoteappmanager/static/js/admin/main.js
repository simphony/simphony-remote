/*globals: require, console*/
require([
  "components/lodash/dist/lodash",
  "components/vue/dist/vue",
  "components/vue-router/dist/vue-router",
  "components/vue-form/dist/vue-form",
  "admin/vue-components/toolkit/toolkit",
  "admin/vue-components/MainView",
  "admin/vue-components/ContainersView",
  "admin/vue-components/UsersView",
  "admin/vue-components/ApplicationsView",
  "admin/vue-components/AccountingView"
], function(
  _,
  Vue, 
  VueRouter,
  VueForm,
  toolkit,
  MainView,
  ContainersView,
  UsersView,
  ApplicationsView,
  AccountingView
  ) {
  
  "use strict";

  // install router
  Vue.use(VueRouter);
  Vue.use(VueForm, {
    inputClasses: {
      valid: 'form-control-success',
      invalid: 'form-control-danger'
    }
  });
  
  Vue.filter("truncate", function(value) {
      return _.truncate(value, {'length': 12 });
    }
  );

  var router = new VueRouter({
    routes: [
      { path: '/', component: MainView },
      { path: '/containers', component: ContainersView },
      { path: '/users', component: UsersView },
      { path: '/users/:id/accounting', component: AccountingView, name: "user_accounting" },
      { path: '/applications', component: ApplicationsView }
    ]
  });

  var vm;
  vm = new Vue({
    el: "#app",
    router: router
  });

});
