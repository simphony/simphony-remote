"use strict";

var Vue = require("vuejs");
var ConfirmDialog = require("./ConfirmDialog");
var ModalDialog = require("./ModalDialog");
var AdminLTEBox = require("./AdminLTEBox");
var DataTable = require("./DataTable");

Vue.component("confirm-dialog", ConfirmDialog);
Vue.component("modal-dialog", ModalDialog);
Vue.component("adminlte-box", AdminLTEBox);
Vue.component("data-table", DataTable);

module.exports = {
    ConfirmDialog: ConfirmDialog,
    AdminLTEBox: AdminLTEBox,
    ModalDialog: ModalDialog,
    DataTable: DataTable
};
