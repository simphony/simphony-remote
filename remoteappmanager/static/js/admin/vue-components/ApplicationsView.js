define([
  "components/vue/dist/vue",
  "jsapi/v1/resources",
  "admin/vue-components/applications/NewApplicationDialog",
  "admin/vue-components/applications/RemoveApplicationDialog",
], function(Vue, resources, NewApplicationDialog, RemoveApplicationDialog) {
  "use strict";

  return {
    components: {
      'new-application-dialog': NewApplicationDialog,
      'remove-application-dialog': RemoveApplicationDialog
    },
    template: 
      '<adminlte-box title="Applications">' +
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
      '    <new-application-dialog ' +
      '      v-if="newApplicationDialog.show"' +
      '      :show="newApplicationDialog.show"' +
      '      @created="newApplicationCreated"' +
      '      @closed="newApplicationDialogClosed"></new-application-dialog>' +
      '      ' +
      '    <remove-application-dialog ' +
      '      v-if="removeApplicationDialog.show"' +
      '      :appToRemove="appToRemove"' +
      '      @removed="appRemoved"' +
      '      @closed="removeDialogClosed"></remove-application-dialog>' +
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
              callback: function() { self.newApplicationDialog.show = true; }
            }
          ],
          rowActions: [
            {
              label: "Remove",
              callback: this.removeAction
            }
          ]
        },
        apps: [],
        newApplicationDialog: {
          show: false
        },
        removeApplicationDialog: {
          show: false
        },
        communicationError: null,
        appToRemove: {
          name: "",
          id: null
        }
      };
    },
    mounted: function () {
      this.updateTable();
    },
    methods: {
      updateTable: function() {
        var self = this;
        this.communicationError = null;
        resources.Application.items()
        .done(
          (function (identifiers, items) {
            self.table.rows = [];
            identifiers.forEach(function(id) {
              var item = items[id];
              self.table.rows.push([
                id,
                item.image_name
              ]);
            });
          }).bind(this))
        .fail(
          (function () {
            this.communicationError = "The request could not be executed successfully";
          }).bind(this)
        );
      },
      newApplicationCreated: function() {
        this.newApplicationDialog.show = false;
        this.updateTable();
      },
      newApplicationDialogClosed: function() {
        this.newApplicationDialog.show = false;
      },
      appRemoved: function() {
        this.removeApplicationDialog.show = false;
        this.updateTable();
      },
      removeAction: function(index) {
        this.appToRemove = this.apps[index];
        this.removeApplicationDialog.show = true;
      },
      removeDialogClosed: function() {
        this.removeApplicationDialog.show = false;
        this.appToRemove = {
          name: "",
          id: null
        };
      }
    }
  };
});

