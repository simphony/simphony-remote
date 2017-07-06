<template>
  <adminlte-box title="Containers">
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
    <confirm-dialog
    v-if="stopContainerDialog.visible"
    title="Stop container"
    :okCallback="stopContainer"
    :closeCallback="closeStopContainerDialog">
      <div>Do you want to stop container {{ stopContainerDialog.containerToStop }}?</div>
    </confirm-dialog>
  </adminlte-box>
</template>

<script>
  let resources = require("admin-resources");
  let _ = require("lodash");

  let truncate = function(value) {
    return _.truncate(value, {'length': 24});
  };

  module.exports = {
    data: function () {
      return {
        table: {
          headers: ["URL ID", "User", "Image", "Docker ID", "Mapping ID"],
          columnFormatters: [truncate, undefined, undefined, truncate, truncate],
          rows: [],
          rowActions: [{
            label: "Stop",
            callback: this.stopAction
          }]
        },
        stopContainerDialog: {
          visible: false,
          containerToStop: null
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
        resources.Container.items()
        .done((identifiers, items) => {
          this.table.rows = [];
          identifiers.forEach((id) => {
            let item = items[id];
            this.table.rows.push([
              id,
              item.user,
              item.image_name,
              item.docker_id,
              item.mapping_id
            ]);
          });
        })
        .fail(() => {
          this.communicationError = "The request could not be executed successfully";
        });
      },

      stopAction: function(row) {
        this.stopContainerDialog.containerToStop = row[0];
        this.stopContainerDialog.visible = true;
      },

      stopContainer: function () {
        let containerToStop = this.stopContainerDialog.containerToStop;
        this.closeStopContainerDialog();
        resources.Container.delete(containerToStop)
        .done(() => {
          this.updateTable();
        })
        .fail(() => {
          this.communicationError = "The request could not be executed successfully";
        });
      },

      closeStopContainerDialog: function() {
        this.stopContainerDialog.visible = false;
        this.stopContainerDialog.containerToStop = null;
      }
    }
  };
</script>
