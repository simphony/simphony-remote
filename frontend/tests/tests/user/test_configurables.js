var configurables = require("user/configurables/configurables");
var Resolution = require("user/configurables/Resolution");

QUnit.module("user.configurables");
QUnit.test("instantiation", function (assert) {
    var resolutionConf = new configurables.resolution();

    assert.equal(resolutionConf.tag, "resolution");
    assert.deepEqual(resolutionConf.configDict, { resolution: "Window" });
    assert.notEqual(resolutionConf.asConfigDict().resolution, "Window");

    resolutionConf.configDict = { resolution: '1280x1024' };
    assert.equal(resolutionConf.asConfigDict().resolution, '1280x1024');
});

QUnit.test("view", function (assert) {
    var propsData = { configDict: { resolution: "Window" } };
    var component = new Resolution({propsData: propsData}).$mount();

    assert.notEqual(component.$el.querySelector("select"), null);
    assert.equal(component.$el.querySelector("select").children.length, 5);
});
