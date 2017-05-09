define([
  "components/vue/dist/vue",
  "jsapi/v1/resources"
], function(Vue, resources) {
  "use strict";
  return {
    template:
      '<modal-dialog>' +
      '    <div class="modal-header"><h4>Remove Accounting</h4></div>' +
      '    <div class="modal-body">Do you want to remove accounting {{ accountingToRemove }}?</div>' +
      '    <div class="modal-footer text-right">' +
      '          <div class="alert alert-danger" v-if="communicationError">' +
      '            <strong>Error:</strong> {{communicationError}}' +
      '          </div>' +
      '        <button type="button" class="btn btn-default" @click="close">Cancel</button>' +
      '        <button class="btn btn-primary primary" @click="okCallback">Remove</button>' +
      '    </div>' +
      '</modal-dialog>',
    props: ['accountingToRemove', "okCallback"],
    data: function() {
      return {
        communicationError: null
      };
    },
    methods: {
      close: function () {
        this.$emit("closed");
      },
    }
  };
});
