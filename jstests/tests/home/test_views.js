define(function (require) {
    "use strict";
    var models = require("home/models");
    var views = require("home/views");
    var $ = require("jquery");

    var MockApi = function () {
        this.available_applications_info = function() {
            return [
                {
                    image : {
                        ui_name : "foo",
                        policy : {
                            allow_home: true
                        }
                    }
                }, 
                {
                    image: {
                        ui_name : "bar",
                        policy : {
                            allow_home: true
                        }
                    }
                }];
        };
    };

    QUnit.module("home.views");
    QUnit.test("rendering", function (assert) {
        var mock_api = new MockApi();
        var model = new models.ApplicationListModel(mock_api);
        var view = new views.ApplicationListView(model);
        model.update()
            .done(function() { view.render(); } )
            .done(function() {
                var applist = $("#applist");
                assert.equal(applist.children().length, 2);
                assert.equal($("#applist > div:nth-child(1) > div > h4").text(), "foo");
                assert.equal($("#applist > div:nth-child(2) > div > h4").text(), "bar");
            });
        
    });
});
