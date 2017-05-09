define([
  "components/vue/dist/vue",
  "admin/vue-components/toolkit/AdminLTEBox",
  "admin/vue-components/toolkit/ModalDialog"
], function(
  Vue,
  AdminLTEBox,
  ModalDialog
) {
  "use strict";
  
  Vue.component("modal-dialog", ModalDialog);
  Vue.component("adminlte-box", AdminLTEBox);
 
  return {
    AdminLTEBox: AdminLTEBox,
    ModalDialog: ModalDialog
  };

}); 
