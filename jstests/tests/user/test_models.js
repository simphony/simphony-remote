var ApplicationListModel = require("user/ApplicationListModel");

QUnit.module("user.ApplicationListModel");
QUnit.test("instantiation", function (assert) {
    var model = new ApplicationListModel();

    assert.equal(model.appList.length, 0);
    assert.equal(model.selectedIndex, null);

    model.update().done(function() {
        assert.equal(model.appList.length, 2);
        assert.equal(model.selectedIndex, 0);

        assert.equal(model.appList[0].appData.image.configurables[0], "resolution");
        assert.equal(model.appList[0].configurables[0].configDict.resolution, "Window");
    });
});
