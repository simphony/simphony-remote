<template>
  <adminlte-box :title="'Accounting for user ' + $route.params.id">
    <div class="alert alert-danger" v-if="communicationError">
      <strong>Error:</strong> {{communicationError}}
    </div>

    <data-table
    :headers.once="table.headers"
    :columnFormatters.once="table.columnFormatters"
    :rows="table.rows"
    :globalActions="table.globalActions"
    :rowActions="table.rowActions">
    </data-table>

    <new-accounting-dialog
    v-if="newAccountingDialog.visible"
    :visible="newAccountingDialog.visible"
    :userId="newAccountingDialog.userId"
    @created="newAccountingCreated"
    @closed="newAccountingDialog.visible = false">
    </new-accounting-dialog>

    <confirm-dialog
    v-if="removeAccountingDialog.visible"
    title="Remove Accounting"
    :okCallback="removeAccounting"
    :closeCallback="closeRemoveAccountingDialog">
      <div>Do you want to remove accounting
        {{ removeAccountingDialog.accountingToRemove }}?
      </div>
    </confirm-dialog>
  </adminlte-box>
</template>

<script>
  let resources = require("admin-resources");
  let NewAccountingDialog = require("./accounting/NewAccountingDialog");

  let checkIconFormatter = function(value) {
    if(value) {
      return '<i class="fa fa-check"></i>';
    }
    return '';
  };

  module.exports = {
    components: {
      'new-accounting-dialog': NewAccountingDialog
    },

    data: function () {
      return {
        table: {
          headers: [
            "ID", "Image", "License", "Workspace", "Vol. source", "Vol. target", "Readonly"
          ],
          columnFormatters: [undefined, undefined, checkIconFormatter, undefined, undefined, checkIconFormatter],
          rows: [],
          globalActions: [{
            label: "Create New Entry",
            callback: () => {this.newAccountingDialog.visible = true;}
          }],
          rowActions: [{
            label: "Remove",
            callback: this.removeAction
          }]
        },

        newAccountingDialog: {
          visible: false,
          userId: this.$route.params.id
        },

        removeAccountingDialog: {
          visible: false,
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
        this.communicationError = null;
        resources.Accounting.items({filter: JSON.stringify({user_id: this.$route.params.id })})
        .done((identifiers, items) => {
          this.table.rows = [];
          identifiers.forEach((id) => {
            let item = items[id];
            this.table.rows.push([
              id,
              item.image_name,
              item.app_license,
              item.allow_home,
              item.volume_source,
              item.volume_target,
              item.volume_mode === "ro",
              item.allow_srdata
            ]);
          });
        })
        .fail(() => {
          this.communicationError = "The request could not be executed successfully";
        });
      },

      newAccountingCreated: function() {
        this.newAccountingDialog.visible = false;
        this.updateTable();
      },

      removeAction: function(row) {
        this.removeAccountingDialog.accountingToRemove = row[0];
        this.removeAccountingDialog.visible = true;
      },

      closeRemoveAccountingDialog: function() {
        this.removeAccountingDialog.visible = false;
        this.removeAccountingDialog.accountingToRemove = null;
      },

      removeAccounting: function () {
        resources.Accounting.delete(this.removeAccountingDialog.accountingToRemove)
        .done(() => {
          this.closeRemoveAccountingDialog();
          this.updateTable();
        })
        .fail(() => {
          this.closeRemoveAccountingDialog();
          this.communicationError = "The request could not be executed successfully";
        });
      }
    },

    watch: {
      '$route.params.id': function() {
        this.table.rows = [];
        this.updateTable();
      }
    }
  };
</script>
