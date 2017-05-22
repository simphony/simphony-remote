let Vue = require("vuejs");
let ConfirmDialog = require("./ConfirmDialog");
let ModalDialog = require("./ModalDialog");
let AdminLTEBox = require("./AdminLTEBox");
let DataTable = require("./DataTable");

Vue.component("confirm-dialog", ConfirmDialog);
Vue.component("modal-dialog", ModalDialog);
Vue.component("adminlte-box", AdminLTEBox);
Vue.component("data-table", DataTable);

module.exports = {
  ConfirmDialog,
  AdminLTEBox,
  ModalDialog,
  DataTable
};
