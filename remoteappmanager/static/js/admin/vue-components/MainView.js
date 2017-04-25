define([
  "components/vue/dist/vue.min"
], function(Vue) {
  "use strict";
  
  return {
    template: `
  <div class="container">
    <div class="row">
    <div class="col-lg-4">Realm</div><div class="col-lg-4">{{ realm }}</div>
  </div>
  <div class="row">
    <div class="col-lg-4">Total users</div><div class="col-lg-8">{{ num_total_users }}</div>
  </div>
  <div class="row">
    <div class="col-lg-4">Number of images</div><div class="col-lg-8">{{ num_images }}</div>
  </div>
  <hr />
  <div class="row">
    <div class="col-lg-4">Active users</div><div class="col-lg-8">{{ num_active_users }}</div>
  </div>
  <div class="row">
    <div class="col-lg-4">Running containers</div><div class="col-lg-8">{{ num_running_containers }}</div>
  </div>
  </div>
  </div>`,
    data: function() {
      return {
        realm: "foo",
        num_total_users: 3,
        num_images: 5,
        num_active_users: 4,
        num_running_containers: 5
      };
    },
    mounted: function() {
      this.$data.realm = "bar";
    }
  };
});
