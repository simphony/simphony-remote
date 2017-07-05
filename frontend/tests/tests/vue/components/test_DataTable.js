var DataTable = require("toolkit").DataTable;
var helpers = require("helpers");

QUnit.module("DataTable");
QUnit.test("rendering", function (assert) {
  assert.equal(helpers.getRenderedText(DataTable, {
    headers: ["foo", "bar"],
    rows: [[1,2], [3,4]],
    rowActions: [{
      label: "Remove",
      callback: function() {}
    }]
  }), "foobar Actions 12 Remove34 Remove");
});
