define([
  "components/vue/dist/vue",
  "admin/vue-components/toolkit/AdminLTEBox",
  "admin/vue-components/toolkit/ConfirmDialog",
  "admin/vue-components/toolkit/ModalDialog",
  "admin/vue-components/toolkit/DataTable"
], function(
  Vue,
  AdminLTEBox,
  ConfirmDialog,
  ModalDialog,
  DataTable
) {
  "use strict";

  Vue.component("confirm-dialog", ConfirmDialog);
  Vue.component("modal-dialog", ModalDialog);
  Vue.component("adminlte-box", AdminLTEBox);
  Vue.component("data-table", DataTable);
 
  return {
    ConfirmDialog: ConfirmDialog,
    AdminLTEBox: AdminLTEBox,
    ModalDialog: ModalDialog,
    DataTable: DataTable
  };

}); 
