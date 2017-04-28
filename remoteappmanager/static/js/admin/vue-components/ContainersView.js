define([
  "components/vue/dist/vue",
  "jsapi/v1/resources",
  "components/lodash/dist/lodash",
  "admin/vue-components/containers/StopContainerDialog"
], function(Vue, resources, _, StopContainerDialog) {
  "use strict";

    return {
      components: {
        'stop-container-dialog': StopContainerDialog
      },
      template: `
<div class="row">
  <div class="col-md-12">
    <div class="box">
      <div class="box-header with-border">Containers</div>
      <div class="box-body">
        <table id="datatable" class="display dataTable">
          <thead>
          <tr>
              <th>User</th>
              <th>Image</th>
              <th>Docker ID</th>
              <th>Mapping ID</th>
              <th>URL ID</th>
              <th>Stop</th>
          </tr>
          </thead>
          <tbody>
            <tr v-for="(c, index) in containers">
              <td>{{ c.user }}</td>
              <td>{{ c.image_name }}</td>
              <td>{{ c.docker_id | truncate }}</td>
              <td>{{ c.mapping_id | truncate }}</td>
              <td>{{ c.identifier | truncate }}</td>
              <td><button class="btn btn-danger" @click="stopAction(index)">Stop</button></td>
            </tr>
          </tbody>
        </table>
        <stop-container-dialog 
          v-if="showStopContainerDialog"
          :containerToStop="containerToStop"
          @stopped="containerStopped"
          @closed="stopContainerDialogClosed"></stop-container-dialog>
      </div>
    </div>
  </div>
</div>`,
      data: function () {
        return {
          containers: [],
          showStopContainerDialog: false,
          containerToStop: null,
        };
      },
      mounted: function () {
        this.updateTable();
      },
      filters: {
        truncate: function(value) {
          return _.truncate(value, {'length': 12 });
        }
      },
      methods: {
        updateTable: function() {
          resources.Container.items()
            .done(
              (function (identifiers, items) {
                var containers = [];
                identifiers.forEach(function(id) {
                  var item = items[id];
                  item.identifier = id;
                  containers.push(item);
                });
                this.containers = containers;
              }).bind(this))
            .fail(function () {
            });
        },
        containerStopped: function() {
          this.showStopContainerDialog = false;
          this.updateTable();
        },
        stopAction: function(index) {
          this.containerToStop = this.containers[index].identifier;
          this.showStopContainerDialog = true;
        },
        stopContainerDialogClosed: function(index) {
          this.showStopContainerDialog = false;
          this.containerToStop = null;
        }
      }
    };
  });
