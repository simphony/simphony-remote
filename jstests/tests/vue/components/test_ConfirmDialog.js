define([
  "components/vue/dist/vue",
  "admin/vue-components/toolkit/ConfirmDialog",
  "jstests/helpers"
], function (Vue, ConfirmDialog, helpers) {
    "use strict";
  
    QUnit.module("ConfirmDialog");
    QUnit.test("rendering", function (assert) {
        assert.equal(helpers.getRenderedText(ConfirmDialog, {
          title: "This is the title"
        }), "This is the title  Cancel Ok");
    });
});
