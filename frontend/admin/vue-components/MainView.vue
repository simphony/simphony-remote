<template>
  <adminlte-box title="Statistics">
    <div class="alert alert-danger" v-if="communicationError">
      <strong>Error:</strong> {{communicationError}}
    </div>
    <table class="table table-bordered">
      <tbody>
        <tr>
          <th>Realm</th>
          <td>{{ realm }}</td>
        </tr>
        <tr>
          <th>Total users</th>
          <td>{{ num_total_users }}</td>
        </tr>
        <tr>
          <th>Number of applications</th>
          <td>{{ num_applications }}</td>
        </tr>
        <tr>
          <th>Active users</th>
          <td>{{ num_active_users }}</td>
        </tr>
        <tr>
          <th>Running containers</th>
          <td>{{ num_running_containers }}</td>
        </tr>
      </tbody>
    </table>
  </adminlte-box>
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
