define([
], function() {
  "use strict";

  return {
    props: [
      "headers", "rows", "globalActions", "rowActions"
    ],
    methods: {
      isBoolean: function(value) {
        return typeof(value) === "boolean";
      },
      buttonClassFromType: function(value) { 
        var cls = {"btn": true};
        if (value === undefined) {
          value = "danger";
        }
        cls["btn-" + value] = true;
        return cls;
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
    '        <td>' +
    '          <button v-for="action in rowActions" ' +
    '                   :class="buttonClassFromType(action.type)"' +
    '                   style="margin-right: 10px"' +
    '                   @click="action.callback(row)">{{action.label}}</button>' +
    '        </td>' +
    '      </tr>' +
    '    </tbody>' +
    '  </table>' +
    '</div>'
  };

});
