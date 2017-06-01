<template>
  <adminlte-box :title="'Accounting for user ' + $route.params.id">
    <div class="alert alert-danger" v-if="communicationError">
      <strong>Error:</strong> {{communicationError}}
    </div>

    <button slot="tools" class="btn btn-primary" @click="newAccountingDialog.visible = true">Create New Entry</button>

    <data-table
    :headers.once="table.headers"
    :rows="table.rows"
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

  module.exports = {
    components: {
      'new-accounting-dialog': NewAccountingDialog
    },

    data: function () {
      return {
        table: {
          headers: [
            "ID", "Image", "Workspace", "Vol. source", "Vol. target", "Readonly"
          ],
          rows: [],
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
              item.allow_home,
              item.volume_source,
              item.volume_target,
              item.volume_mode === "ro"
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
    }
  };
</script>
