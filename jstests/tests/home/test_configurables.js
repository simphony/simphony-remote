define([
    "jquery",
    "home/configurables"
], function ($, configurables) {
    "use strict";

    QUnit.module("home.configurables");
    QUnit.test("instantiation", function (assert) {
        var resolution = $.extend(true, {}, configurables["resolution"]);

        assert.equal(resolution.tag, "resolution");
        assert.equal(resolution.value, "Window");

        resolution.value = "1024x768";
        assert.equal(resolution.as_config_dict().resolution, "1024x768");
    });
});