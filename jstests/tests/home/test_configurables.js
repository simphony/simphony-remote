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
        var component = new configurables.resolution_component().$mount();

        assert.notEqual(component.$el.querySelector("select"), null);
        assert.equal(component.$el.querySelector("select").children.length, 5);

        component.selected_value = '1280x1024';
        assert.equal(component.as_config_dict().resolution.resolution, '1280x1024');
    });
});