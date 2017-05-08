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
      '<div class="row">' +
      '  <div class="col-md-12">' +
      '    <div class="box">' +
      '      <div class="box-header with-border">Applications</div>' +
      '      <div class="box-body">' +
      '        <div class="alert alert-danger" v-if="communicationError">' +
      '          <strong>Error:</strong> {{communicationError}}' +
      '        </div>' +
      '        <div class="pull-right">' +
      '          <button class="btn btn-primary createnew" @click="showNewApplicationDialog = true">Create New</button>' +
      '        </div>' +
      '        <table id="datatable" class="display dataTable">' +
      '          <thead>' +
      '          <tr>' +
      '              <th>ID</th>' +
      '              <th>Image</th>' +
      '              <th>Remove</th>' +
      '          </tr>' +
      '          </thead>' +
      '          <tbody>' +
      '            <tr v-for="(a, index) in apps">' +
      '              <td>{{ a.id }}</td>' +
      '              <td>{{ a.image_name }}</td>' +
      '              <td><button class="btn btn-danger" @click="removeAction(index)">Remove</button></td>' +
      '            </tr>' +
      '          </tbody>' +
      '        </table>' +
      '        <new-application-dialog ' +
      '          v-if="showNewApplicationDialog"' +
      '          :show="showNewApplicationDialog"' +
      '          @created="newApplicationCreated"' +
      '          @closed="newApplicationDialogClosed"></new-application-dialog>' +
      '          ' +
      '        <remove-application-dialog ' +
      '          v-if="showRemoveApplicationDialog"' +
      '          :appToRemove="appToRemove"' +
      '          @removed="appRemoved"' +
      '          @closed="removeDialogClosed"></remove-application-dialog>' +
      '      </div>' +
      '    </div>' +
      '  </div>' +
      '</div>',
    data: function () {
      return {
        apps: [],
        showNewApplicationDialog: false,
        showRemoveApplicationDialog: false,
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
        this.communicationError = null;
        resources.Application.items()
        .done(
          (function (identifiers, items) {
            var apps = [];
            identifiers.forEach(function(id) {
              apps.push({
                id: id,
                image_name: items[id].image_name
              });
            });
            this.apps = apps;
          }).bind(this))
        .fail(
          (function () {
            this.communicationError = "The request could not be executed successfully";
          }).bind(this)
        );
      },
      newApplicationCreated: function() {
        this.showNewApplicationDialog = false;
        this.updateTable();
      },
      newApplicationDialogClosed: function() {
        this.showNewApplicationDialog = false;
      },
      appRemoved: function() {
        this.showRemoveApplicationDialog = false;
        this.updateTable();
      },
      removeAction: function(index) {
        this.appToRemove = this.apps[index];
        this.showRemoveApplicationDialog = true;
      },
      removeDialogClosed: function() {
        this.showRemoveApplicationDialog = false;
        this.appToRemove = {
          name: "",
          id: null
        };
      }
    }
  };
});

