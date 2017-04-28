/*globals: require, console*/
require([
  "components/vue/dist/vue",
  "components/vue-router/dist/vue-router",
  "components/vue-form/dist/vue-form",
  "admin/vue-components/MainView",
  "admin/vue-components/ContainersView",
  "admin/vue-components/UsersView",
  "admin/vue-components/ApplicationsView"
], function(
  Vue, 
  VueRouter,
  VueForm,
  MainView,
  ContainersView,
  UsersView,
  ApplicationsView) {
  
  "use strict";

  // install router
  Vue.use(VueRouter);
  Vue.use(VueForm, {
    inputClasses: {
      valid: 'form-control-success',
      invalid: 'form-control-danger'
    }
  });
  
  const router = new VueRouter({
    routes: [
      { path: '/', component: MainView },
      { path: '/containers', component: ContainersView },
      { path: '/users', component: UsersView },
      { name: "user_accounting", path: '/users/:id/accounting', component: UsersView },
      { path: '/applications', component: ApplicationsView }
    ]
  });

  Vue.component("modal",
    {
      template: `
        <transition name="modal">
          <div class="modal-mask">
            <div class="modal-wrapper">
              <div class="modal-container">
                <slot>
                </slot>
              </div>
            </div>
          </div>
        </transition>`,
    });
  
  const app = new Vue({
    router
  }).$mount('#app');

});
