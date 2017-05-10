define([
  "components/vue/dist/vue",
  "jsapi/v1/resources"
], function(Vue, resources) {
  "use strict";
  return {
    template: 
      '<modal-dialog>' +
      '  <div class="modal-header"><h4>Remove Application</h4></div>' +
      '  <div class="modal-body">Do you want to remove application {{ appToRemove.image_name }}?</div>' +
      '  <div class="modal-footer text-right">' +
      '    <div class="alert alert-danger" v-if="communicationError">' +
      '      <strong>Error:</strong> {{communicationError}}' +
      '    </div>' +
      '    <button type="button" class="btn btn-default" @click="close">Cancel</button>' +
      '    <button class="btn btn-primary primary" @click="removeApplication">Remove</button>' +
      '  </div>' +
      '</modal-dialog>',
    props: ['appToRemove'],
    data: function() {
      return {
        communicationError: null
      };
    },
    methods: {
      close: function () {
        this.$emit("closed");
      },
      removeApplication: function () {
        if (this.appToRemove.id === null) {
          this.$emit("closed");
          return;
        }
        resources.Application.delete(this.appToRemove.id)
          .done((function () {
            this.$emit("removed");
          }).bind(this))
          .fail(
            (function () {
              this.communicationError = "The request could not be executed successfully";
            }).bind(this)
          );
      }
    }
  };
});
