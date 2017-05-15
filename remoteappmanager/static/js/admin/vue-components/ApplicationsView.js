var Vue = require("vuejs");
var resources = require("resources");
var NewApplicationDialog = require("./applications/NewApplicationDialog");

module.exports = {
    components: {
        'new-application-dialog': NewApplicationDialog
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
        '    <confirm-dialog ' +
        '      v-if="removeApplicationDialog.show"' +
        '      title="Remove Application"' +
        '      :okCallback="removeApplication"' +
        '      :closeCallback="closeRemoveApplicationDialog">' +
        '      <div>Do you want to remove Application ' +
        '           {{removeApplicationDialog.applicationToRemove.name}} ' +
        '          ({{removeApplicationDialog.applicationToRemove.id}})</div>' +
        '    </confirm-dialog>' +
        '  </div>' +
        '</adminlte-box>',

    data: function () {
        var self=this;
        return {
            table: {
                headers: ["ID", "Image"],
                rows: [],
                globalActions: [{
                    label: "Create New Entry",
                    callback: function() { self.newApplicationDialog.show = true; }
                }],
                rowActions: [{
                    label: "Remove",
                    callback: this.removeAction
                }]
            },

            newApplicationDialog: {
                show: false
            },

            removeApplicationDialog: {
                show: false,
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
            var self = this;
            this.communicationError = null;
            resources.Application.items()
            .done(function (identifiers, items) {
                self.table.rows = [];
                identifiers.forEach(function(id) {
                    var item = items[id];
                    self.table.rows.push([
                        id,
                        item.image_name
                    ]);
                });
            })
            .fail(function () {
                self.communicationError = "The request could not be executed successfully";
            });
        },

        newApplicationCreated: function() {
            this.newApplicationDialog.show = false;
            this.updateTable();
        },

        newApplicationDialogClosed: function() {
            this.newApplicationDialog.show = false;
        },

        removeAction: function(row) {
            this.removeApplicationDialog.applicationToRemove = {
                id: row[0],
                name: row[1]
            };
            this.removeApplicationDialog.show = true;
        },

        removeApplication: function () {
            var self = this;
            resources.Application.delete(this.removeApplicationDialog.applicationToRemove.id)
            .done(function () {
                self.closeRemoveApplicationDialog();
                self.updateTable();
            })
            .fail(function () {
                self.closeRemoveApplicationDialog();
                this.communicationError = "The request could not be executed successfully";
            });
        },
        closeRemoveApplicationDialog: function() {
            this.removeApplicationDialog.show = false;
            this.removeApplicationDialog.applicationToRemove = {
                name: "",
                id: null
            };
        }
    }
};

