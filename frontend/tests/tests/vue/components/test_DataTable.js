let DataTable = require("toolkit").DataTable;
let helpers = require("helpers");
let _ = require("lodash");

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

  let checkIconFormatter = function(value) {
    return '<i class="fa fa-check" v-if="' + value + '"></i>';
  };

  let truncate = function(value) {
    return _.truncate(value, {'length': 24});
  };

  assert.equal(helpers.getRenderedText(DataTable, {
    headers: ["ID", "name", "checked"],
    rows: [
      ["12345678901234567890123456789", "JohnDoe", false],
      ["98765432109876543210987654321", "JaneDoe", true]
    ],
    columnFormatters: [truncate, undefined, checkIconFormatter]
  }).trim(), "IDnamechecked  123456789012345678901...JohnDoe 987654321098765432109...JaneDoe");
});
