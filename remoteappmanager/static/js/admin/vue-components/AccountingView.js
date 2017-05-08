define([
  "components/vue/dist/vue",
  "jsapi/v1/resources",
  "admin/vue-components/accounting/NewAccountingDialog",
  "admin/vue-components/accounting/RemoveAccountingDialog"
], function(Vue, resources, NewAccountingDialog, RemoveAccountingDialog) {
  "use strict";

  return {
    components: {
      'new-accounting-dialog': NewAccountingDialog,
      'remove-accounting-dialog': RemoveAccountingDialog
    },
    template: 
      '  <adminlte-box>' +
      '        <div slot="header">Accounting for user {{ $route.params.id }} </div>' +
      '        <div slot="body">' +
      '          <div class="alert alert-danger" v-if="communicationError">' +
      '            <strong>Error:</strong> {{communicationError}}' +
      '          </div>' +
      '          <div class="pull-right">' +
      '            <button class="btn btn-primary createnew" @click="showNewAccountingDialog = true">Create New</button>' +
      '          </div>' +
      '          <table id="datatable" class="display dataTable">' +
      '            <thead>' +
      '            <tr>' +
      '                <th>ID</th>' +
      '                <th>Image</th>' +
      '                <th>Workspace</th>' +
      '                <th>Vol. source</th>' +
      '                <th>Vol. target</th>' +
      '                <th>Readonly</th>' +
      '                <th>Remove</th>' +
      '            </tr>' +
      '            </thead>' +
      '            <tbody>' +
      '              <tr v-for="(a, index) in accountings">' +
      '                <td>{{ a.identifier | truncate }}</td>' +
      '                <td>{{ a.image_name }}</td>' +
      '                <td class="dt-center"><i v-show="a.allow_home" class="fa fa-check" aria-hidden="true"></i></td>' +
      '                <td>{{ a.volume_source }}</td>' +
      '                <td>{{ a.volume_target }}</td>' +
      '                <td class="dt-center"><i v-show="a.volume_mode == '+"'"+'ro'+"'"+'" class="fa fa-check" aria-hidden="true"></i></td>' +
      '                <td><button class="btn btn-danger" @click="removeAction(index)">Remove</button></td>' +
      '              </tr>' +
      '            </tbody>' +
      '          </table>' +
      '          <new-accounting-dialog ' +
      '            v-if="showNewAccountingDialog"' +
      '            :show="showNewAccountingDialog"' +
      '            :userId="userId"' +
      '            @created="newAccountingCreated"' +
      '            @closed="newAccountingDialogClosed"></new-accounting-dialog>' +
      '            ' +
      '          <remove-accounting-dialog ' +
      '            v-if="showRemoveAccountingDialog"' +
      '            :accToRemove="accToRemove"' +
      '            @removed="accRemoved"' +
      '            @closed="removeDialogClosed"></remove-accounting-dialog>' +
      '        </div>' +
      '  </adminlte-box>',
    data: function () {
      return {
        accountings: [],
        showNewAccountingDialog: false,
        showRemoveAccountingDialog: false,
        userId: this.$route.params.id,
        communicationError: null,
        accToRemove: {
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
        resources.Accounting.items({filter: JSON.stringify({user_id: this.$route.params.id })})
        .done(
          (function (identifiers, items) {
            var accountings = [];
            identifiers.forEach(function(id) {
              var item = items[id];
              item.identifier = id;
              accountings.push(item);
            });
            this.accountings = accountings;
          }).bind(this))
        .fail(
          (function () {
            this.communicationError = "The request could not be executed successfully";
          }).bind(this)
        );
      },
      newAccountingCreated: function() {
        this.showNewAccountingDialog = false;
        this.updateTable();
      },
      newAccountingDialogClosed: function() {
        this.showNewAccountingDialog = false;
      },
      accRemoved: function() {
        this.showRemoveAccountingDialog = false;
        this.updateTable();
      },
      removeAction: function(index) {
        this.accToRemove = {id: this.accountings[index].identifier};
        this.showRemoveAccountingDialog = true;
      },
      removeDialogClosed: function() {
        this.showRemoveAccountingDialog = false;
        this.accToRemove = {
          id: null
        };
      }
    }
  };
});

