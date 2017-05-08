define([
  "components/vue/dist/vue",
  "jsapi/v1/resources",
  "admin/vue-components/accounting/NewAccountingDialog",
  "admin/vue-components/accounting/RemoveAccountingDialog"
], function(Vue, resources, NewAccountingDialog, RemoveAccountingDialog) {
  "use strict";

  return {
    components: {
      'new-accounting-dialog': NewAccountingDialog,
      'remove-accounting-dialog': RemoveAccountingDialog
    },
    template: 
      '  <adminlte-box>' +
      '        <div slot="header">Accounting for user {{ $route.params.id }} </div>' +
      '        <div slot="body">' +
      '          <div class="alert alert-danger" v-if="communicationError">' +
      '            <strong>Error:</strong> {{communicationError}}' +
      '          </div>' +
      '          <data-table' +
      '           :headers.once="headers"' +
      '           :rows="rows"' +
      '           :globalActions="globalActions"' +
      '           :rowActions="rowActions">' +
      '          </data-table>' +
      '          <new-accounting-dialog ' +
      '            v-if="showNewAccountingDialog"' +
      '            :show="showNewAccountingDialog"' +
      '            :userId="userId"' +
      '            @created="newAccountingCreated"' +
      '            @closed="newAccountingDialogClosed"></new-accounting-dialog>' +
      '            ' +
      '          <remove-accounting-dialog ' +
      '            v-if="showRemoveAccountingDialog"' +
      '            :accToRemove="accToRemove"' +
      '            @removed="accRemoved"' +
      '            @closed="removeDialogClosed"></remove-accounting-dialog>' +
      '        </div>' +
      '  </adminlte-box>',
    data: function () {
      var self = this;
      return {
        headers: [
          "ID", "Image", "Workspace", "Vol. source", "Vol. target", "Readonly"
        ],
        rows: [],
        globalActions: [
          {
            label: "Create New Entry",
            callback: function() { self.showNewAccountingDialog = true; }
          }
        ],
        rowActions: [
          {
            label: "Remove",
            callback: this.removeAction
          }
        ],
        showNewAccountingDialog: false,
        showRemoveAccountingDialog: false,
        userId: this.$route.params.id,
        communicationError: null,
        accToRemove: {
          id: null
        }
      };
    },
    mounted: function () {
      this.updateTable();
    },
    methods: {
      updateTable: function() {
        var self = this;
        this.communicationError = null;
        resources.Accounting.items({filter: JSON.stringify({user_id: this.$route.params.id })})
        .done(
          function (identifiers, items) {
            identifiers.forEach(function(id) {
              var item = items[id];
              self.rows.push([
                id, 
                item.image_name, 
                item.allow_home, 
                item.volume_source,
                item.volume_target,
                item.volume_mode === "ro"]);
            });
          })
        .fail(
          function () {
            self.communicationError = "The request could not be executed successfully";
          }
        );
      },
      newAccountingCreated: function() {
        this.showNewAccountingDialog = false;
        this.updateTable();
      },
      newAccountingDialogClosed: function() {
        this.showNewAccountingDialog = false;
      },
      accRemoved: function() {
        this.showRemoveAccountingDialog = false;
        this.updateTable();
      },
      removeAction: function(row) {
        this.accToRemove = {id: row[0]};
        this.showRemoveAccountingDialog = true;
      },
      removeDialogClosed: function() {
        this.showRemoveAccountingDialog = false;
        this.accToRemove = {
          id: null
        };
      }
    }
  };
});

