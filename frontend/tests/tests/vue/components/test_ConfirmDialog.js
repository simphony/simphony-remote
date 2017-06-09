var ConfirmDialog = require("toolkit").ConfirmDialog;
var helpers = require("helpers");

QUnit.module("ConfirmDialog");
QUnit.test("rendering", function (assert) {
  assert.equal(helpers.getRenderedText(ConfirmDialog, {
    title: "This is the title",
    closeCallback: function() {}
  }), "This is the title  Cancel Ok");

  assert.equal(helpers.getRenderedText(ConfirmDialog, {
    title: "This is the title"
  }), "This is the title   Ok");
});
