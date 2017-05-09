define([
  "components/vue/dist/vue",
  "jsapi/v1/resources",
  "admin/vue-components/containers/StopContainerDialog"
], function(Vue, resources, StopContainerDialog) {
  "use strict";

    return {
      components: {
        'stop-container-dialog': StopContainerDialog
      },
      template: 
        '<adminlte-box title="Containers">' +
        '  <div class="alert alert-danger" v-if="communicationError">' +
        '    <strong>Error:</strong> {{communicationError}}' +
        '  </div>' +
        '  <data-table' +
        '    :headers.once="table.headers"' +
        '    :rows="table.rows"' +
        '    :globalActions="table.globalActions"' +
        '    :rowActions="table.rowActions">' +
        '  </data-table>' +
        '  <stop-container-dialog ' +
        '    v-if="stopContainerDialog.show"' +
        '    :containerToStop="stopContainerDialog.containerToStop"' +
        '    @stopped="containerStopped"' +
        '    @closed="stopContainerDialogClosed"></stop-container-dialog>' +
        '</adminlte-box>',
      data: function () {
        return {
          table: {
            headers: ["URL ID", "User", "Image", "Docker ID", "Mapping ID"],
            rows: [],
            rowActions: [
              {
                label: "Stop",
                callback: this.stopAction
              }
            ]
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
          var self=this;
          this.communicationError = null;
          resources.Container.items()
            .done(
              (function (identifiers, items) {
                self.table.rows = [];
                identifiers.forEach(function(id) {
                  var item = items[id];
                  self.table.rows.push([
                    id,
                    item.user,
                    item.image_name,
                    item.docker_id,
                    item.mapping_id]);
                });
              }))
            .fail(
              function () {
                self.communicationError = "The request could not be executed successfully";
              }
            );
        },
        containerStopped: function() {
          this.stopContainerDialog.show = false;
          this.updateTable();
        },
        stopAction: function(row) {
          this.stopContainerDialog.containerToStop = row[0];
          this.stopContainerDialog.show = true;
        },
        stopContainerDialogClosed: function() {
          this.stopContainerDialog.show = false;
          this.stopContainerDialog.containerToStop = null;
        }
      }
    };
  });
