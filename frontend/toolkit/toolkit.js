let Vue = require("vue");
let ConfirmDialog = require("./ConfirmDialog");
let ModalDialog = require("./ModalDialog");
let AdminLTEBox = require("./AdminLTEBox");
let DataTable = require("./DataTable");
let ErrorDialog = require("./ErrorDialog");
require("./filters");

Vue.component("confirm-dialog", ConfirmDialog);
Vue.component("modal-dialog", ModalDialog);
Vue.component("adminlte-box", AdminLTEBox);
Vue.component("data-table", DataTable);
Vue.component("error-dialog", ErrorDialog);

module.exports = {
  ConfirmDialog,
  AdminLTEBox,
  ModalDialog,
  DataTable,
  ErrorDialog
};
