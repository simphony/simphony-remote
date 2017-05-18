<template>
  <div class="row">
    <div class="col-md-12">
      <div class="box">
        <div class="box-header with-border">Statistics</div>
        <div class="box-body">
          <div class="alert alert-danger" v-if="communicationError">
            <strong>Error:</strong> {{communicationError}}
          </div>
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
  </div>
</template>

<script>
  let resources = require("admin-resources");

  module.exports = {
    data: function() {
      return {
        communicationError: null,
        realm: "",
        num_total_users: "",
        num_applications: "",
        num_active_users: "",
        num_running_containers: ""
      };
    },

    mounted: function() {
      resources.Stats.retrieve()
      .done((rep) => {
        this.realm = rep.realm;
        this.num_total_users = rep.num_total_users;
        this.num_applications = rep.num_applications;
        this.num_active_users = rep.num_active_users;
        this.num_running_containers = rep.num_running_containers;
      })
      .fail(() => {
        this.communicationError = "The request could not be executed successfully";
      });
    }
  };
</script>
