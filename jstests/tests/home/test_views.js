define([
    "home/models",
    "home/views/application_list_view", 
    "jquery"
], function (models, application_list_view, $) {
    "use strict";
    QUnit.module("home.views");
    QUnit.test("rendering", function (assert) {
        var model = new models.ApplicationListModel();
        var view = new application_list_view.ApplicationListView(model);
        model.update()
            .done(function() { view.render(); } )
            .done(function() {
                var applist = $("#applist");
                assert.equal(applist.children().length, 2);
            })
            .done(function() {
                model.app_data[0].image.ui_name = "Hello";
                view.update_entry(0);
            });
    });
});
