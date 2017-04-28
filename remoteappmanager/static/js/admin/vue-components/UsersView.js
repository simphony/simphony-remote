define([
  "jquery",
  "components/vue/dist/vue",
  "jsapi/v1/resources"
], function($, Vue, resources) {
  "use strict";

  var NewUserDialog = {
    template: `
      <modal>
        <div class="modal-header"><h4>Create New User</h4></div>
        <div class="modal-body">
          <vue-form :state="formstate" v-model="formstate" @submit.prevent="createNewUser">
            <validate auto-label class="form-group required-field" :class="fieldClassName(formstate.name)">
              <label class="control-label">User Name</label>
              <input type="text" name="name" class="form-control" required v-model="model.name">

              <field-messages name="name" show="$touched || $submitted">
                <span class="help-block" slot="required">User Name cannot be empty</span>
              </field-messages>
            </validate>

            <div class="modal-footer">
              <button type="button" class="btn btn-default" @click="close()">Cancel</button>
              <button class="btn btn-primary" type="submit" :disabled="formstate.$invalid">Submit</button>
            </div>
          </vue-form> 
        </div>
    </modal>`,
    props: ['show'],
    
    data: function () {
      return {
        formstate: {},
        model: {
          name: ''
        }
      };
    },
    methods: {
      close: function () {
        this.$emit('closed');
      },
      fieldClassName: function (field) {
        if(!field) {
          return '';
        }
        if((field.$touched || field.$submitted) && field.$invalid) {
          return 'has-error';
        } else {
          return '';
        }
      },
      createNewUser: function() {
        if (! this.formstate.$valid) {
          return;
        }
        var user_name = $.trim(this.model.name);
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
      },
      reset: function() {
         Object.assign(this.$data, this.$options.data());
      }
    },
    watch: {
      "show": function(value) {
        if (value) {
          this.reset();
        }
      }
    }
  };

  var RemoveUserDialog = {
    template: `
    <modal>
        <div class="modal-header"><h4>Remove User</h4></div>
        <div class="modal-body">Do you want to remove user {{ userToRemove.name }}?</div>

        <div class="modal-footer text-right">
            <button type="button" class="btn btn-default" @click="close">Cancel</button>
            <button class="btn btn-primary primary" @click="removeUser">Remove</button>
        </div>
    </modal>
    `,
    props: ['userToRemove'],
    methods: {
      close: function () {
        this.$emit("closed");
      },
      removeUser: function() {
        if (this.userToRemove.id === null) {
          this.$emit("closed");
          return;
        }
        resources.User.delete(this.userToRemove.id)
        .done((function () {
          this.$emit("removed");
        }).bind(this))
        .fail(
          (function () {
            this.$emit("closed");
          }).bind(this)
        );
      }
    }
  };

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
