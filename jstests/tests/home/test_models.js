define([
    "home/models", 
    "../../../../../jstests/tests/home/mock_remoteappapi"
], function (models, mock_api) {
    "use strict";

    QUnit.module("home.models");
    QUnit.test("instantiation", function (assert) {
        var api = new mock_api.MockApi();
        var model = new models.ApplicationListModel(api);
        assert.equal(model.app_data.length, 0);
        model.update().done(function() {
            assert.equal(model.app_data.length, 2);
            assert.equal(model.app_data[0].image.configurables[0], "resolution");
            assert.notEqual(model.configurables[0].resolution, null);
            assert.equal(model.configurables[0].resolution.resolution, "Window");
        });
    });
});

