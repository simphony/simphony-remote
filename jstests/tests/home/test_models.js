define(function (require) {
    "use strict";
    var models = require("home/models");
    var mock_api = require("../../../../../jstests/tests/home/mock_remoteappapi");

    QUnit.module("home.models");
    QUnit.test("instantiation", function (assert) {
        var api = new mock_api.MockApi();
        var model = new models.ApplicationListModel(api);
        assert.equal(model.data.length, 0);
        model.update().done(function() {
            assert.equal(model.data.length, 2);
            assert.equal(model.data[0].image.configurables[0], "resolution");
            assert.equal(model.data[0].image.configurables_data.resolution, null);
        });
    });
});
