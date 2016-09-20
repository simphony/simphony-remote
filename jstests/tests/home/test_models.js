define(function (require) {
    "use strict";
    var models = require("home/models");

    var MockApi = function () {
        this.available_applications_info = function() {
            return [{}, {}];
        };
    };

    QUnit.module("home.models");
    QUnit.test("instantiation", function (assert) {
        var mock_api = new MockApi();
        var model = new models.ApplicationListModel(mock_api);
        assert.equal(model.data.length, 0);
        model.update().done(function() {
            assert.equal(model.data.length, 2);
        });
    });
});
