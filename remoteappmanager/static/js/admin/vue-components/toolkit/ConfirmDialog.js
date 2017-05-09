define([
], function() {
  "use strict";
  
  return {
    props: {
      title: {
        type: String,
        default: "Confirm"
      },
      closeCallback: {
        type: Function,
        default: function() {}
      },
      okCallback: {
        type: Function,
        default: function() {}
      },
      errorMessage: {
        type: String,
        default: ""
      }
    },
    template: '<transition name="modal">' +
    '  <div class="modal-mask">' +
    '    <div class="modal-wrapper">' +
    '      <div class="modal-container">' +
    '        <div class="modal-header"><slot name="header"><h4>{{ title }}</h4></slot></div>' +
    '        <div class="modal-body"><slot></slot></div>' +
    '        <div class="modal-footer text-right">' +
    '          <button type="button" class="btn btn-default" @click="closeCallback">Cancel</button>' +
    '          <button class="btn btn-primary primary" @click="okCallback">Ok</button>' +
    '        </div>' +
    '      </div>' +
    '    </div>' +
    '  </div>' +
    '</transition>'
  };
});
