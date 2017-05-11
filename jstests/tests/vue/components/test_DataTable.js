define([
  "components/vue/dist/vue",
  "admin/vue-components/toolkit/DataTable",
  "jstests/helpers"
], function (Vue, DataTable, helpers) {
    "use strict";
  
    QUnit.module("DataTable");
    QUnit.test("rendering", function (assert) {
        assert.equal(helpers.getRenderedText(DataTable, {
          headers: ["foo", "bar"],
          rows: [[1,2], [3,4]],
          globalActions: [{
            label: "New",
            callback: function() {}
          }],
          rowActions: [{
            label: "Remove",
            callback: function() {}
          }]
        }), "New foobar Actions 12 Remove34 Remove");
    });
});
