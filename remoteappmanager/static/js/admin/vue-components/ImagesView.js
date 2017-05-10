define([
  "components/vue/dist/vue",
  "jsapi/v1/resources",
  "admin/vue-components/images/NewImageDialog"
], function(Vue, resources, NewImageDialog) {
  "use strict";

  return {
    components: {
      'new-image-dialog': NewImageDialog
    },
    template: 
      '<adminlte-box title="Images">' +
      '  <div>' +
      '    <div class="alert alert-danger" v-if="communicationError">' +
      '      <strong>Error:</strong> {{communicationError}}' +
      '    </div>' +
      '    <data-table' +
      '       :headers.once="table.headers"' +
      '       :rows="table.rows"' +
      '       :globalActions="table.globalActions"' +
      '       :rowActions="table.rowActions">' +
      '    </data-table>' +
      '    <new-image-dialog ' +
      '      v-if="newImageDialog.show"' +
      '      :show="newImageDialog.show"' +
      '      @created="newImageCreated"' +
      '      @closed="newImageDialogClosed"></new-image-dialog>' +
      '      ' +
      '    <confirm-dialog ' +
      '      v-if="removeImageDialog.show"' +
      '      title="Remove Image"' +
      '      :okCallback="removeImage"' +
      '      :closeCallback="closeRemoveImageDialog">' +
      '      <div>Do you want to remove Image' +
      '           {{removeImageDialog.imageToRemove.name}} ' +
      '          ({{removeImageDialog.imageToRemove.id}})</div>' +
      '    </confirm-dialog>' +
      '  </div>' +
      '</adminlte-box>',
    data: function () {
      var self=this;
      return {
        table: {
          headers: ["ID", "Image"],
          rows: [],
          globalActions: [
            {
              label: "Create New Entry",
              callback: function() { self.newImageDialog.show = true; }
            }
          ],
          rowActions: [
            {
              label: "Remove",
              callback: this.removeAction
            }
          ]
        },
        newImageDialog: {
          show: false
        },
        removeImageDialog: {
          show: false,
          imageToRemove: {
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
        var self = this;
        this.communicationError = null;
        resources.Image.items()
        .done(
          function (identifiers, items) {
            self.table.rows = [];
            identifiers.forEach(function(id) {
              var item = items[id];
              self.table.rows.push([
                id,
                item.image_name
              ]);
            });
          })
        .fail(
          function () {
            self.communicationError = "The request could not be executed successfully";
          }
        );
      },
      newImageCreated: function() {
        this.newImageDialog.show = false;
        this.updateTable();
      },
      newImageDialogClosed: function() {
        this.newImageDialog.show = false;
      },
      removeAction: function(row) {
        this.removeImageDialog.imageToRemove = {
          id: row[0],
          name: row[1]
        };
        this.removeImageDialog.show = true;
      },
      removeImage: function () {
        var self = this; 
        resources.Image.delete(this.removeImageDialog.imageToRemove.id)
          .done(function () {
            self.closeRemoveImageDialog();
            self.updateTable();
          })
          .fail(
            function () {
              self.closeRemoveImageDialog();
              this.communicationError = "The request could not be executed successfully";
            }
          );
      },
      closeRemoveImageDialog: function() {
        this.removeImageDialog.show = false;
        this.removeImageDialog.imageToRemove = {
          name: "",
          id: null
        };
      }
    }
  };
});

