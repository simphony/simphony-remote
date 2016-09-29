define(function(require) {
    "use strict";
    var analytics = require("analytics");
    
    QUnit.module("Google Analytics");
    QUnit.test("test without analytics", function (assert) {
        window.apidata.analytics = undefined;
        var ga = analytics.init();
        assert.equal(window.ga.l, undefined);
    });
    
    QUnit.test("test with analytics", function (assert) {
        window.apidata.analytics = {"tracking_id": "X"};
        var ga = analytics.init();
        assert.notEqual(window.ga.l, undefined);
    });
});
