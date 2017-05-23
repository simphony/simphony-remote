var DataTable = require("toolkit-dir/DataTable");
var helpers = require("helpers");

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
