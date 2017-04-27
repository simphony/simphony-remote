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
      <div class="box-header with-border">Users</div>
      <div class="box-body">
        <table id="datatable" class="display dataTable">
          <thead>
          <tr>
              <th>ID</th>
              <th>Username</th>
              <th>Accounting</th>
              <th>Remove</th>
          </tr>
          </thead>
          <tbody>
            <tr v-for="u in users">
              <td>{{ u.id }}</td>
              <td>{{ u.name }}</td>
              <td> <router-link :to="{ name: 'user_accounting', params: { id: u.id }}">Show</router-link></td>
              <td><button class="btn btn-danger"
                          data-value="{{ u.id }}"
                          data-name="{{ u.name }}"
                          data-toggle="modal"
                          data-target="#action-dialog">Remove</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</div>`,
    data: function () {
      return {
        users: []
      };
    },
    mounted: function () {
      resources.User.items()
        .done(
          (function (identifiers, items) {
            var users = [];
            identifiers.forEach(function(id) {
              users.push({
                id: id,
                name: items[id].name
              });
            })
            this.$data.users = users;
          }).bind(this))
        .fail(function () {
        });
    }
  };
});
