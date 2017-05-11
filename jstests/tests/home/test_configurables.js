define([
    "home/configurables"
], function (configurables) {
    "use strict";

    QUnit.module("home.configurables");
    QUnit.test("instantiation", function (assert) {
        var resolution_conf = new configurables.resolution();

        assert.equal(resolution_conf.tag, "resolution");
        assert.deepEqual(resolution_conf.config_dict, { resolution: "Window" });
        assert.notEqual(resolution_conf.as_config_dict().resolution, "Window");

        resolution_conf.config_dict = { resolution: '1280x1024' };
        assert.equal(resolution_conf.as_config_dict().resolution, '1280x1024');
    });

    QUnit.test("view", function (assert) {
        var propsData = { config_dict: { resolution: "Window" } };
        var component = new configurables.resolution_component({propsData: propsData}).$mount();

        assert.notEqual(component.$el.querySelector("select"), null);
        assert.equal(component.$el.querySelector("select").children.length, 5);
    });
});