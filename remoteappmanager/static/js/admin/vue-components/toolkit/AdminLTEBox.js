define([
  "components/vue/dist/vue"
], function(Vue) {
  "use strict";
  
  return {
    props: {
      title: {
        type: String,
        default: "Box"
      }
    },
    template:
    '  <div class="row">' +
    '    <div class="col-md-12">' +
    '      <div class="box">' +
    '        <div class="box-header with-border"><slot name="header">{{title}}</slot></div>' +
    '        <div class="box-body"><slot></slot></div>' +
    '      </div>' +
    '    </div>' +
    '  </div>'
  };
  
});
