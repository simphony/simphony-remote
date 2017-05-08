require([
  "components/vue/dist/vue"
], function(Vue) {
  "use strict";

  Vue.component("data-table", {
    props: [
      "headers", "rows", "globalActions", "rowActions"
    ],
    methods: {
      "isBoolean": function(value) {
        return typeof(value) === "boolean";
      }
    },
    template:
    '<div>' +
    '  <div class="pull-right">' +
    '    <button v-for="action in globalActions" class="btn btn-primary" @click="action.callback">{{action.label}}</button>' +
    '  </div>' +
    '  <table id="datatable" class="display dataTable">' +
    '    <thead>' +
    '    <tr>' +
    '        <th v-for="header in headers">{{header}}</th>' +
    '        <th v-if="rowActions.length > 0">Actions</th>' +
    '    </tr>' +
    '    </thead>' +
    '    <tbody>' +
    '      <tr v-for="(row, row_index) in rows">' +
    '        <template v-for="(value, col_index) in row">' +
    '          <td v-if="isBoolean(value)"><i class="fa fa-check" v-if="value"></i></td>' +
    '          <td v-else>{{value}}</td>' +
    '        </template>' +
    '        <td v-for="action in rowActions">' +
    '          <button class="btn btn-danger" @click="action.callback(row)">{{action.label}}</button></td>' +
    '        </td>' +
    '      </tr>' +
    '    </tbody>' +
    '  </table>' +
    '</div>'
  });

});
