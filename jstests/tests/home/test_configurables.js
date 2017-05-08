define([
    "home/configurables"
], function (configurables) {
    "use strict";

    QUnit.module("home.configurables");
    QUnit.test("instantiation", function (assert) {
        var resolution = new configurables.resolution();

        assert.equal(resolution.tag, "resolution");
        assert.equal(resolution.value, "Window");

        resolution.value = "1024x768";
        assert.equal(resolution.as_config_dict().resolution, "1024x768");
    });

    QUnit.test("view", function (assert) {
        var resolution = new configurables.resolution();
        var component = new resolution.component().$mount("#resolution-configurable");

        assert.notEqual(component.$el.querySelector("select"), null);
        assert.equal(component.$el.querySelector("select").children.length, 5);
    });
});