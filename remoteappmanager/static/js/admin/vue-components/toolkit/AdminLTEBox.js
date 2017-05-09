define([
  "components/vue/dist/vue"
], function(Vue) {
  "use strict";
  
  return {
    template:
    '  <div class="row">' +
    '    <div class="col-md-12">' +
    '      <div class="box">' +
    '        <div class="box-header with-border"><slot name="header"></slot></div>' +
    '        <div class="box-body"><slot name="body"></slot></div>' +
    '      </div>' +
    '    </div>' +
    '  </div>'
  };
  
});
