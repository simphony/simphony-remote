define([
    "home/configurables"
], function (configurables) {
    "use strict";

    QUnit.module("home.configurables");
    QUnit.test("instantiation", function (assert) {
        var resolution_class = configurables.from_tag("resolution");
        var resolution = new resolution_class();
        assert.equal(resolution.tag, "resolution");
        assert.equal(resolution.resolution, "Window");
        
        resolution.resolution = "1024x768";
        assert.equal(resolution.as_config_dict().resolution, "1024x768");
    });
    
    QUnit.test("view", function (assert) {
        var resolution_class = configurables.from_tag("resolution");
        var resolution = new resolution_class();

        var view = resolution.view();
        assert.notEqual(view.find("select"), null);
        assert.equal(view.find("option").length, 
            resolution.resolution_options.length);
    });
});
