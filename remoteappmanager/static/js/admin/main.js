let _ = require("lodash");
let Vue = require("vuejs");
let VueRouter = require("vue-router");
let VueForm = require("vue-form");
require("toolkit");
let MainView = require("./vue-components/MainView");
let ContainersView = require("./vue-components/ContainersView");
let UsersView = require("./vue-components/UsersView");
let ApplicationsView = require("./vue-components/ApplicationsView");
let AccountingView = require("./vue-components/AccountingView");

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
});

let router = new VueRouter({
  routes: [
    { path: '/', component: MainView },
    { path: '/containers', component: ContainersView },
    { path: '/users', component: UsersView },
    { path: '/users/:id/accounting', component: AccountingView, name: "user_accounting" },
    { path: '/applications', component: ApplicationsView }
  ]
});

let vm;
vm = new Vue({
  el: "#app",
  router: router
});
