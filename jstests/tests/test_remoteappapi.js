define([
    "require", 
    "remoteappapi"
], function (require, RemoteAppAPI) {
    QUnit.module("Remote App API");
    QUnit.test("test", function (assert) {
        var api = new RemoteAppAPI();
        assert.ok(api !== null);
    });
});
