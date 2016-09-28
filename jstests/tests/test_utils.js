define([
	"utils"
], function (utils) {
	QUnit.module("Utils");
	QUnit.test("url_path_join", function (assert) { 
        assert.equal(utils.url_path_join("foo", "bar", "baz"), "foo/bar/baz");
	});
});
