define(["require", "jquery"], function (require, $) {
    var RemoteAppAPI = require("remoteappapi");
    var mock_api_request = function(result) {
        "use strict";
        return $.Deferred();
    };
    QUnit.module("Remote App API");
    QUnit.test("test", function (assert) {
        var api = new RemoteAppAPI();
        assert.ok(api !== null);
    });
});
