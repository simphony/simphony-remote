define(function(require) {
    "use strict";
    var analytics = require("analytics");
    
    QUnit.module("Google Analytics");
    QUnit.test("test without analytics", function (assert) {
        var result=[];
        window.ga = function(cmd, id, auto) {
            result[0] = [cmd, id, auto];
        };
        window.apidata.analytics = undefined;
        var ga = analytics.init();
        assert.equal(result.length, 0);
    });
    
    QUnit.test("test with analytics", function (assert) {
        var result=[];
        window.ga = function(cmd, id, auto) {
            result[0] = [cmd, id, auto];
        };
        window.apidata.analytics = {"tracking_id": "X"};
        var ga = analytics.init();
        assert.equal(result[0][0], "create");
        assert.equal(result[0][1], "X");
        assert.equal(result[0][2], "auto");
    });
});
