define([
    "home/models"
], function (models) {
    "use strict";

    QUnit.module("home.models");
    QUnit.test("instantiation", function (assert) {
        var model = new models.ApplicationListModel();
        assert.equal(model.app_list.length, 0);
        model.update().done(function() {
            assert.equal(model.app_list.length, 2);
            assert.equal(model.app_list[0].app_data.image.configurables[0], "resolution");
            assert.equal(model.app_list[0].configurables[0].config_dict.resolution, "Window");
        });
    });
});

