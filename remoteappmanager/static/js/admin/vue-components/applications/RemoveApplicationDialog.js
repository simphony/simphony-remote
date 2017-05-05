define([
  "components/vue/dist/vue",
  "jsapi/v1/resources"
], function(Vue, resources) {
  "use strict";
  return {
    template: 
      '<modal>' +
      '    <div class="modal-header"><h4>Remove Application</h4></div>' +
      '    <div class="modal-body">Do you want to remove application {{ appToRemove.image_name }}?</div>' +
      '    <div class="modal-footer text-right">' +
      '        <button type="button" class="btn btn-default" @click="close">Cancel</button>' +
      '        <button class="btn btn-primary primary" @click="removeApplication">Remove</button>' +
      '    </div>' +
      '</modal>',
    props: ['appToRemove'],
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
              this.$emit("closed");
            }).bind(this)
          );
      }
    }
  };
});
