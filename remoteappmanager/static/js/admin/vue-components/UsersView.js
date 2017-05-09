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
    template: 
      '<adminlte-box title="Users">' +
      '    <div class="alert alert-danger" v-if="communicationError">' +
      '      <strong>Error:</strong> {{communicationError}}' +
      '    </div>' +
      '    <data-table' +
      '     :headers.once="table.headers"' +
      '     :rows="table.rows"' +
      '     :globalActions="table.globalActions"' +
      '     :rowActions="table.rowActions">' +
      '    </data-table>' +
      '    <new-user-dialog ' +
      '      v-if="newUserDialog.show"' +
      '      :show="newUserDialog.show"' +
      '      @created="newUserCreated"' +
      '      @closed="newUserDialogClosed"></new-user-dialog>' +
      '    <remove-user-dialog ' +
      '      v-if="removeUserDialog.show"' +
      '      :userToRemove="removeUserDialog.userToRemove"' +
      '      @removed="userRemoved"' +
      '      @closed="removeDialogClosed"></remove-user-dialog>' +
      '</adminlte-box>',
    data: function () {
      var self = this;
      return {
        table: {
          headers: ["ID", "Username"],
          rows: [],
          globalActions: [
            {
              label: "Create New Entry",
              callback: function() { self.newUserDialog.show = true; }
            }
          ],
          rowActions: [
            {
              label: "Policies",
              callback: this.showPolicyAction,
              type: "info"
            },
            {
              label: "Remove",
              callback: this.removeAction,
            }
          ]
        },
        users: [],
        newUserDialog: {
          show: false,
          userToRemove: {
            name: "",
            id: null
          }
        },
        removeUserDialog: {
          show: false
        },
        communicationError: null
      };
    },
    mounted: function () {
      this.updateTable();
    },
    methods: {
      updateTable: function() {
        var self = this;
        this.communicationError = null;
        resources.User.items()
        .done(
          function (identifiers, items) {
            identifiers.forEach(function(id) {
              var item = items[id];
              self.table.rows.push([
                id,
                item.name
              ]);
            });
          })
        .fail(
          function () {
            self.communicationError = "The request could not be executed successfully";
           });
      },
      newUserCreated: function() {
        this.newUserDialog.show = false;
        this.updateTable();
      },
      newUserDialogClosed: function() {
        this.newUserDialog.show = false;
      },
      userRemoved: function() {
        this.removeUserDialog.show = false;
        this.updateTable();
      },
      removeAction: function(row) {
        this.removeUserDialog.userToRemove.id = row[0];
        this.removeUserDialog.userToRemove.name = row[1];
        this.removeUserDialog.show = true;
      },
      showPolicyAction: function(row) {
        this.$router.push({
          name: 'user_accounting',
          params: { id: row[0] }
        });
      },
      removeDialogClosed: function() {
        this.removeUserDialog.show = false;
        this.userToRemove = {
          name: "",
          id: null
        };
      }
    }
  };
});
