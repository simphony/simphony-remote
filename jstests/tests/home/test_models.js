define([
    "home/models"
], function (models) {
    "use strict";

    QUnit.module("home.models");
    QUnit.test("instantiation", function (assert) {
        var model = new models.ApplicationListModel();
        assert.equal(model.appList.length, 0);
        model.update().done(function() {
            assert.equal(model.appList.length, 2);
            assert.equal(model.appList[0].appData.image.configurables[0], "resolution");
            assert.equal(model.appList[0].configurables[0].resolution, "Window");
        });
    });
});

