<template>
  <adminlte-box title="Applications">
    <div class="alert alert-danger" v-if="communicationError">
      <strong>Error:</strong> {{communicationError}}
    </div>

    <data-table
    :headers.once="table.headers"
    :rows="table.rows"
    :globalActions="table.globalActions"
    :rowActions="table.rowActions">
    </data-table>

    <confirm-dialog
    v-if="removeApplicationDialog.visible"
    title="Remove Application"
    :okCallback="removeApplication"
    :closeCallback="closeRemoveApplicationDialog">
      <div>Do you want to remove Application
        {{removeApplicationDialog.applicationToRemove.name}}
        ({{removeApplicationDialog.applicationToRemove.id}})</div>
    </confirm-dialog>
  </adminlte-box>
</template>

<script>
  let resources = require("admin-resources");

  module.exports = {
    data: function () {
      return {
        table: {
          headers: ["ID", "Image"],
          rows: [],
          rowActions: [{
            label: "Remove",
            callback: this.removeAction
          }, {
            label: "Add",
            type: "primary",
            callback: this.addApplication
          }]
        },

        newApplicationDialog: {
          visible: false
        },

        removeApplicationDialog: {
          visible: false,
          applicationToRemove: {
            id: null,
            name: ""
          }
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
        resources.Application.items()
        .done((identifiers, items) => {
          this.table.rows = [];
          identifiers.forEach((id) => {
            let item = items[id];
            this.table.rows.push([
              item.db_image ? id: "-",
              item.image_name
            ]);
          });
        })
        .fail(() => {
          this.communicationError = "The request could not be executed successfully";
        });
      },

      removeAction: function(row) {
        this.removeApplicationDialog.applicationToRemove = {
          id: row[0],
          name: row[1]
        };
        this.removeApplicationDialog.visible = true;
      },

      removeApplication: function () {
        resources.Application.delete(this.removeApplicationDialog.applicationToRemove.id)
        .done(() => {
          this.closeRemoveApplicationDialog();
          this.updateTable();
        })
        .fail(() => {
          this.closeRemoveApplicationDialog();
          this.communicationError = "The request could not be executed successfully";
        });
      },

      closeRemoveApplicationDialog: function() {
        this.removeApplicationDialog.visible = false;
        this.removeApplicationDialog.applicationToRemove = {
          name: "",
          id: null
        };
      },

      addApplication: function(row) {
        resources.Application.create({image_name: row[1]})
        .done(() => {
          this.updateTable();
        })
        .fail(() => {
          this.communicationError = "The request could not be executed successfully";
        });
      }
    }
  };
</script>
