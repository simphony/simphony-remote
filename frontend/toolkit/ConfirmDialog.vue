<template>
  <modal-dialog>
    <div class="modal-header"><slot name="header"><h4>{{ title }}</h4></slot></div>
    <div class="modal-body"><slot></slot></div>
    <div class="modal-footer text-right">
      <button v-if="closeCallback !== undefined" type="button" class="btn btn-default" @click="closeCallback">Cancel</button>
      <button class="btn btn-primary primary" @click="okCallback">Ok</button>
    </div>
  </modal-dialog>
</template>

<script>
  require('./ModalDialog');
</script>

<script>
  module.exports = {
    props: {
      title: {
        type: String,
        default: "Confirm"
      },
      closeCallback: {
        type: Function,
        default: undefined
      },
      okCallback: {
        type: Function,
        default: function() {}
      }
    }
  };
</script>
