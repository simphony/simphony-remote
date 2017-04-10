define([
    "urlutils"
], function (urlutils) {
    QUnit.module("URL Utils");
    QUnit.test("path_join", function (assert) {
        assert.equal(urlutils.url_path_join("foo", "bar", "baz"), "foo/bar/baz");
    });
});
