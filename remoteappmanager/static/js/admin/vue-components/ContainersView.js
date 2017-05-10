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
        '  <confirm-dialog ' +
        '    v-if="stopContainerDialog.show"' +
        '    title="Stop container"' +
        '    :okCallback="stopContainer"' +
        '    :closeCallback="closeStopContainerDialog">' +
        '    <div>Do you want to stop container {{ stopContainerDialog.containerToStop }}?</div>' +
        '  </confirm-dialog>' +
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
              function (identifiers, items) {
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
              })
            .fail(
              function () {
                self.communicationError = "The request could not be executed successfully";
              }
            );
        },
        stopAction: function(row) {
          this.stopContainerDialog.containerToStop = row[0];
          this.stopContainerDialog.show = true;
        },
        stopContainer: function () {
          if (this.stopContainerDialog.containerToStop === null) {
            return;
          }
          var self = this;
          resources.Container.delete(this.stopContainerDialog.containerToStop)
            .done(function () {
              self.updateTable();
              self.closeContainerDialog();
            })
            .fail(
              function () {
                self.closeStopContainerDialog();
                self.communicationError = "The request could not be executed successfully";
              }
            );
        },
        closeStopContainerDialog: function() {
          this.stopContainerDialog.show = false;
          this.stopContainerDialog.containerToStop = null;
        }
      }
    };
  });
