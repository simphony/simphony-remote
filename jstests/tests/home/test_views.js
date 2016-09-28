define(function (require) {
    "use strict";
    var models = require("home/models");
    var views = require("home/views");
    var mock_api = require("../../../../../jstests/tests/home/mock_remoteappapi");
    var $ = require("jquery");

    QUnit.module("home.views");
    QUnit.test("rendering", function (assert) {
        var api = new mock_api.MockApi();
        var model = new models.ApplicationListModel(api);
        var view = new views.ApplicationListView(model);
        model.update()
            .done(function() { view.render(); } )
            .done(function() {
                var applist = $("#applist");
                assert.equal(applist.children().length, 2);
                assert.equal($("#applist > div:nth-child(1) > div > h4").text(), "Application 1");
                assert.equal($("#applist > div:nth-child(2) > div > h4").text(), "Application 2");
            })
            .done(function() {
                model.app_data[0].image.ui_name = "Hello";
                view.update_entry(0);
                assert.equal($("#applist > div:nth-child(1) > div > h4").text(), "Hello");
            });
    });
});
