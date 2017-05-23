var utils = require("utils");

QUnit.module("Utils");
QUnit.test("update", function (assert) {
  var o1 = {"foo": "bar"};
  var o2 = {"bar": "baz"};

  utils.update(o1, o2);

  assert.deepEqual(o1, {
    "foo": "bar",
    "bar": "baz"
  });
});
