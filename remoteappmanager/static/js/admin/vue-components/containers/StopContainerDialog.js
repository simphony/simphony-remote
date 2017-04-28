define([
  "components/vue/dist/vue",
  "jsapi/v1/resources"
], function(Vue, resources) {
  "use strict";
  return {
    template: `
      <modal>
          <div class="modal-header"><h4>Stop Container</h4></div>
          <div class="modal-body">Do you want to stop container {{ containerToStop }}?</div>

          <div class="modal-footer text-right">
              <button type="button" class="btn btn-default" @click="close">Cancel</button>
              <button class="btn btn-primary primary" @click="stopContainer">Stop</button>
          </div>
      </modal>
      `,
    props: ['containerToStop'],
    methods: {
      close: function () {
        this.$emit("closed");
      },
      stopContainer: function () {
        if (this.containerToStop === null) {
          this.$emit("closed");
          return;
        }
        resources.Container.delete(this.containerToStop)
          .done((function () {
            this.$emit("stopped");
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
