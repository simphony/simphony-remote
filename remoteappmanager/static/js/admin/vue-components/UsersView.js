define([
  "jquery",
  "components/vue/dist/vue.min",
  "jsapi/v1/resources"
], function($, Vue, resources) {
  "use strict";

  return {
    template: `
<div class="row">
  <div class="col-md-12">
    <div class="box">
      <div class="box-header with-border">Users</div>
      <div class="box-body">
        <div class="pull-right">
          <button class="btn btn-primary createnew"
                  data-toggle="modal"
                  data-target="#create-new-dialog">Create New</button>
        </div>
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
        <div class="modal fade" id="create-new-dialog" tabindex="-1" role="dialog" aria-labelledby="create-new-label" aria-hidden="true">
          <div class="modal-dialog">
            <div class="modal-content">
              <div class="modal-header">
                <button type="button" class="close modal-close" data-dismiss="modal"><span aria-hidden="true">&times;</span><span class="sr-only">Close</span></button>
                <h4 class="modal-title" id="create-new-label">Create New User</h4>
              </div>
              <div class="modal-body">
                <form>
                    <label for="user-name">User name</label>
                    <input type="text" class="form-control" id="user-name" v-model="new_name">
                    <div class="alert alert-danger" role="alert" v-show="new_name.length === 0">User name cannot be empty</div>
                </form>
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-default modal-close" data-dismiss="modal">Cancel</button>
                <button type="button" 
                        class="btn btn-primary primary" 
                        data-dismiss="modal" 
                        :disabled="new_name.length === 0"
                        @click="createNewUser">Create</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
`,
    data: function () {
      return {
        users: [],
        new_name: "hello",
      };
    },
    mounted: function () {
      this.update();
    },
    methods: {
      update: function() {
        resources.User.items()
          .done(
            (function (identifiers, items) {
              var users = [];
              identifiers.forEach(function(id) {
                users.push({
                  id: id,
                  name: items[id].name
                });
              });
              this.$data.users = users;
            }).bind(this))
          .fail(function () {
          });
      },
      createNewUser: function() {
        var user_name = $.trim(this.$data.new_name);
        resources.User.create({ name: user_name })
          .done((function() { this.update(); }).bind(this))
          .fail(function() {});
      }
    }
  };
});
