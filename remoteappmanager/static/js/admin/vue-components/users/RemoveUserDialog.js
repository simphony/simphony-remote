define([
  "components/vue/dist/vue",
  "jsapi/v1/resources"
], function(Vue, resources) {
  "use strict";
  return {
    template: 
      '<modal>' +
      '    <div class="modal-header"><h4>Remove User</h4></div>' +
      '    <div class="modal-body">Do you want to remove user {{ userToRemove.name }}?</div>' +
      '    <div class="modal-footer text-right">' +
      '        <button type="button" class="btn btn-default" @click="close">Cancel</button>' +
      '        <button class="btn btn-primary primary" @click="removeUser">Remove</button>' +
      '    </div>' +
      '</modal>',
    props: ['userToRemove'],
    methods: {
      close: function () {
        this.$emit("closed");
      },
      removeUser: function () {
        if (this.userToRemove.id === null) {
          this.$emit("closed");
          return;
        }
        resources.User.delete(this.userToRemove.id)
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
