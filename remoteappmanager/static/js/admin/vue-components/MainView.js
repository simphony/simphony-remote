define([
  "components/vue/dist/vue.min",
  "jsapi/v1/resources"
], function(Vue, resources) {
  "use strict";
  
  return {
    template: 
      '<div class="row">' +
      '  <div class="col-md-12">' +
      '    <div class="box">' +
      '      <div class="box-header with-border">Statistics</div>' +
      '      <div class="box-body">' +
      '        <div class="alert alert-danger" v-if="communicationError">' +
      '          <strong>Error:</strong> {{communicationError}}' +
      '        </div>' +
      '        <div class="container">' +
      '          <div class="row">' +
      '            <div class="col-lg-4">Realm</div>' +
      '            <div class="col-lg-4">{{ realm }}</div>' +
      '          </div>' +
      '          <div class="row">' +
      '            <div class="col-lg-4">Total users</div>' +
      '            <div class="col-lg-8">{{ num_total_users }}</div>' +
      '          </div>' +
      '          <div class="row">' +
      '            <div class="col-lg-4">Number of images</div>' +
      '            <div class="col-lg-8">{{ num_images }}</div>' +
      '          </div>' +
      '          <hr />' +
      '          <div class="row">' +
      '            <div class="col-lg-4">Active users</div>' +
      '            <div class="col-lg-8">{{ num_active_users }}</div>' +
      '          </div>' +
      '          <div class="row">' +
      '            <div class="col-lg-4">Running containers</div>' +
      '            <div class="col-lg-8">{{ num_running_containers }}</div>' +
      '          </div>' +
      '        </div>' +
      '      </div>' +
      '    </div>' +
      '  </div>' +
      '</div>',
    data: function() {
      return {
        communicationError: null,
        realm: "",
        num_total_users: "",
        num_images: "",
        num_active_users: "",
        num_running_containers: ""
      };
    },
    mounted: function() {
      resources.Stats.retrieve()
        .done(
          (function(rep) {
          this.$data.realm = rep.realm;
          this.$data.num_total_users = rep.num_total_users;
          this.$data.num_images = rep.num_images;
          this.$data.num_active_users = rep.num_active_users;
          this.$data.num_running_containers = rep.num_running_containers;
        }).bind(this)
        )
        .fail(
          (function() {
            this.communicationError = "The request could not be executed successfully";
          }).bind(this)

        );
    }
  };
});
