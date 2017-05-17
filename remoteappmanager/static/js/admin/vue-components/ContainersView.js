let resources = require("admin-resources");

module.exports = {
  template:
    `<adminlte-box title="Containers">
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
      v-if="stopContainerDialog.show"
      title="Stop container"
      :okCallback="stopContainer"
      :closeCallback="closeStopContainerDialog">
      <div>Do you want to stop container {{ stopContainerDialog.containerToStop }}?</div>
      </confirm-dialog>
    </adminlte-box>`,

  data: function () {
    return {
      table: {
        headers: ["URL ID", "User", "Image", "Docker ID", "Mapping ID"],
        rows: [],
        rowActions: [{
          label: "Stop",
          callback: this.stopAction
        }]
      },
      stopContainerDialog: {
        show: false,
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
      this.stopContainerDialog.show = true;
    },

    stopContainer: function () {
      resources.Container.delete(this.stopContainerDialog.containerToStop)
      .done(() => {
        this.updateTable();
        this.closeStopContainerDialog();
      })
      .fail(() => {
        this.closeStopContainerDialog();
        this.communicationError = "The request could not be executed successfully";
      });
    },

    closeStopContainerDialog: function() {
      this.stopContainerDialog.show = false;
      this.stopContainerDialog.containerToStop = null;
    }
  }
};
