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
      '           :headers.once="table.headers"' +
      '           :rows="table.rows"' +
      '           :globalActions="table.globalActions"' +
      '           :rowActions="table.rowActions">' +
      '          </data-table>' +
      '          <new-accounting-dialog ' +
      '            v-if="newAccountingDialog.show"' +
      '            :show="newAccountingDialog.show"' +
      '            :userId="newAccountingDialog.userId"' +
      '            @created="newAccountingCreated"' +
      '            @closed="newAccountingDialogClosed"></new-accounting-dialog>' +
      '            ' +
      '          <remove-accounting-dialog ' +
      '            v-if="removeAccountingDialog.show"' +
      '            :accountingToRemove="removeAccountingDialog.accountingToRemove"' +
      '            :okCallback="removeAccounting"' +
      '            @closed="removeDialogClosed"></remove-accounting-dialog>' +
      '        </div>' +
      '  </adminlte-box>',
    data: function () {
      var self = this;
      return {
        table: {
          headers: [
            "ID", "Image", "Workspace", "Vol. source", "Vol. target", "Readonly"
          ],
          rows: [],
          globalActions: [
            {
              label: "Create New Entry",
              callback: function() { self.newAccountingDialog.show = true; }
            }
          ],
          rowActions: [
            {
              label: "Remove",
              callback: this.removeAction
            }
          ]
        },
        newAccountingDialog: {
          show: false,
          userId: this.$route.params.id
        },
        removeAccountingDialog: {
          show: false,
          accountingToRemove: null
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
        resources.Accounting.items({filter: JSON.stringify({user_id: this.$route.params.id })})
        .done(
          function (identifiers, items) {
            self.table.rows = [];
            identifiers.forEach(function(id) {
              var item = items[id];
              self.table.rows.push([
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
        this.newAccountingDialog.show = false;
        this.updateTable();
      },
      newAccountingDialogClosed: function() {
        this.newAccountingDialog.show = false;
      },
      removeAction: function(row) {
        this.removeAccountingDialog.accountingToRemove = row[0];
        this.removeAccountingDialog.show = true;
      },
      removeDialogClosed: function() {
        this.removeAccountingDialog.show = false;
        this.accountingToRemove = null;
      },
      removeAccounting: function () {
        if (this.removeAccountingDialog.accountingToRemove === null) {
          return;
        }
        resources.Accounting.delete(this.removeAccountingDialog.accountingToRemove)
          .done((function () {
              this.removeDialogClosed();
              this.updateTable();
          }).bind(this))
          .fail(
            (function () {
              this.communicationError = "The request could not be executed successfully";
            }).bind(this)
          );
      }
    }
  };
});

