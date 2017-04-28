define([
  "components/vue/dist/vue",
  "jsapi/v1/resources",
  "admin/vue-components/users/NewUserDialog",
  "admin/vue-components/users/RemoveUserDialog",
], function(Vue, resources, NewUserDialog, RemoveUserDialog) {
  "use strict";

  return {
    components: {
      'new-user-dialog': NewUserDialog,
      'remove-user-dialog': RemoveUserDialog
    },
    template: `
<div class="row">
  <div class="col-md-12">
    <div class="box">
      <div class="box-header with-border">Users</div>
      <div class="box-body">
        <div class="pull-right">
          <button class="btn btn-primary createnew" @click="showNewUserDialog = true">Create New</button>
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
            <tr v-for="(u, index) in users">
              <td>{{ u.id }}</td>
              <td>{{ u.name }}</td>
              <td><router-link :to="{ name: 'user_accounting', params: { id: u.id }}">Show</router-link></td>
              <td><button class="btn btn-danger" @click="removeAction(index)">Remove</button></td>
            </tr>
          </tbody>
        </table>
        <new-user-dialog 
          v-if="showNewUserDialog"
          :show="showNewUserDialog"
          @created="newUserCreated"
          @closed="newUserDialogClosed"></new-user-dialog>
          
        <remove-user-dialog 
          v-if="showRemoveUserDialog"
          :userToRemove="userToRemove"
          @removed="userRemoved"
          @closed="removeDialogClosed"></remove-user-dialog>
      </div>
    </div>
  </div>
</div>`,
    data: function () {
      return {
        users: [],
        showNewUserDialog: false,
        showRemoveUserDialog: false,
        userToRemove: {
          name: "",
          id: null
        }
      };
    },
    mounted: function () {
      this.updateTable();
    },
    methods: {
      updateTable: function() {
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
            this.users = users;
          }).bind(this))
        .fail(function () {
        });
      },
      newUserCreated: function() {
        this.showNewUserDialog = false;
        this.updateTable();
      },
      newUserDialogClosed: function() {
        this.showNewUserDialog = false;
      },
      userRemoved: function() {
        this.showRemoveUserDialog = false;
        this.updateTable();
      },
      removeAction: function(index) {
        this.userToRemove = this.users[index];
        this.showRemoveUserDialog = true;
      },
      removeDialogClosed: function(index) {
        this.showRemoveUserDialog = false;
        this.userToRemove = {
          name: "",
          id: null
        };
      }
    }
  };
});
