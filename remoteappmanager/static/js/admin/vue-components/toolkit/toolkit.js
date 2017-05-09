define([
  "components/vue/dist/vue",
  "admin/vue-components/toolkit/AdminLTEBox",
  "admin/vue-components/toolkit/ModalDialog",
  "admin/vue-components/toolkit/DataTable"
], function(
  Vue,
  AdminLTEBox,
  ModalDialog,
  DataTable
) {
  "use strict";
  
  Vue.component("modal-dialog", ModalDialog);
  Vue.component("adminlte-box", AdminLTEBox);
  Vue.component("data-table", DataTable);
 
  return {
    AdminLTEBox: AdminLTEBox,
    ModalDialog: ModalDialog,
    DataTable: DataTable
  };

}); 
