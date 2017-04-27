define([
  "components/vue/dist/vue.min",
  "jsapi/v1/resources"
], function(Vue, resources) {
  "use strict";
  
  return {
    template: `
<div class="row">
  <div class="col-md-12">
    <div class="box">
      <div class="box-header with-border">Statistics</div>
      <div class="box-body">
        <div class="container">
          <div class="row">
            <div class="col-lg-4">Realm</div>
            <div class="col-lg-4">{{ realm }}</div>
          </div>
          <div class="row">
            <div class="col-lg-4">Total users</div>
            <div class="col-lg-8">{{ num_total_users }}</div>
          </div>
          <div class="row">
            <div class="col-lg-4">Number of applications</div>
            <div class="col-lg-8">{{ num_applications }}</div>
          </div>
          <hr />
          <div class="row">
            <div class="col-lg-4">Active users</div>
            <div class="col-lg-8">{{ num_active_users }}</div>
          </div>
          <div class="row">
            <div class="col-lg-4">Running containers</div>
            <div class="col-lg-8">{{ num_running_containers }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>`,
    data: function() {
      return {
        realm: "",
        num_total_users: "",
        num_applications: "",
        num_active_users: "",
        num_running_containers: ""
      };
    },
    mounted: function() {
      resources.Stats.retrieve()
        .done((function(rep) { 
          this.$data.realm = rep.realm;
          this.$data.num_total_users = rep.num_total_users;
          this.$data.num_applications = rep.num_applications;
          this.$data.num_active_users = rep.num_active_users;
          this.$data.num_running_containers = rep.num_running_containers;
        }).bind(this));
    }
  };
});
