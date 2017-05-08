define([
    "home/configurables"
], function (configurables) {
    "use strict";

    QUnit.module("home.configurables");
    QUnit.test("instantiation", function (assert) {
        var resolution = new configurables.resolution();

        assert.equal(resolution.tag, "resolution");
        assert.equal(resolution.value, "Window");
    });

    QUnit.test("view", function (assert) {
        var component = new configurables.resolution_component().$mount("#resolution-configurable");

        assert.notEqual(component.$el.querySelector("select"), null);
        assert.equal(component.$el.querySelector("select").children.length, 5);
    });
});