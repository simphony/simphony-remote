var _ = require("lodash");
var Vue = require("vuejs");
var VueRouter = require("vue-router");
var VueForm = require("vue-form");
require("toolkit");
var MainView = require("./vue-components/MainView");
var ContainersView = require("./vue-components/ContainersView");
var UsersView = require("./vue-components/UsersView");
var ApplicationsView = require("./vue-components/ApplicationsView");
var AccountingView = require("./vue-components/AccountingView");

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
