define([
  "jquery",
  "components/vue/dist/vue.min",
  "jsapi/v1/resources"
], function($, Vue, resources) {
  "use strict";

  Vue.component('new-user-dialog', {
    template: `
      <modal :show="show" :on-close="close">
         <div class="modal-header"><h4>Create New User</h4></div>
         <div class="modal-body">
         <form>
         <label for="user-name">User name</label>
          <input type="text" class="form-control" id="user-name" v-model="name">
          <div class="alert alert-danger" role="alert" v-show="name.length === 0">User name cannot be empty</div>
         </form>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-default" @click="close()">Cancel</button>
          <button type="button" class="btn btn-primary primary" :disabled="name.length === 0" @click="createNewUser">Create</button>
        </div>
    </modal>`,
    props: ['show'],
    data: function () {
      return {
        name: ''
      };
    },
    methods: {
      close: function () {
        this.$emit('closed');
      },
      createNewUser: function() {
        var user_name = $.trim(this.name);
        resources.User.create({ name: user_name })
        .done((
          function() {
            this.$emit('created');
          }).bind(this)
        )
        .fail(
          (function() {
            this.$emit("closed");
          }).bind(this)
        );
      }
    }
  });

  Vue.component('remove-user-dialog', {
    template: `
    <modal :show="show" :on-close="close">
        <div class="modal-header"><h4>Remove User</h4></div>
        <div class="modal-body">Do you want to remove the user?</div>

        <div class="modal-footer text-right">
            <button type="button" class="btn btn-default" @click="close()">Cancel</button>
            <button class="btn btn-primary primary" @click="removeUser()">Remove</button>
        </div>
    </modal>
    `,
    props: ['show'],
    data: function () {
      return {
        id: null
      };
    },
    methods: {
      close: function () {
        this.id = null;
        this.$emit("closed");
      },
      removeUser: function() {
        resources.User.delete(this.id)
          .done((function() {
            this.$emit("removed");
          }).bind(this))
          .fail(
            (function() {
              this.$emit("closed");
            }).bind(this)
          );
        this.close();
      }
    }
  });


  return {
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
            <tr v-for="u in users">
              <td>{{ u.id }}</td>
              <td>{{ u.name }}</td>
              <td><router-link :to="{ name: 'user_accounting', params: { id: u.id }}">Show</router-link></td>
              <td><button class="btn btn-danger" @click="showRemoveUserDialog = true">Remove</button></td>
            </tr>
          </tbody>
        </table>
        <new-user-dialog 
          :show="showNewUserDialog"
          v-on:created="newUserCreated"
          v-on:closed="showNewUserDialog=false"></new-user-dialog>
          
        <remove-user-dialog 
          :show="showRemoveUserDialog"
          v-on:removed="userRemoved"
          v-on:closed="showRemoveUserDialog=false"></remove-user-dialog>
      </div>
    </div>
  </div>
</div>`,
    data: function () {
      return {
        users: [],
        showNewUserDialog: false,
        showRemoveUserDialog: false
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
      newUserCreated: function() {
        this.showNewUserDialog = false;
        this.update();
      },
      userRemoved: function() {
        this.showRemoveUserDialog = false;
        this.update();
      }
    },
  };
});


