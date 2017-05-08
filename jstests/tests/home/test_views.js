define([
    "home/models",
    "home/views/application_list_view",
    "jquery"
], function (models, application_list_view, $) {
    "use strict";
    QUnit.module("home.views");
    QUnit.test("rendering", function (assert) {
        assert.expect(2);

        var model = new models.ApplicationListModel();
        var view = new application_list_view.ApplicationListView(
            { model: model }
        );

        assert.ok(model.loading);

        model.update()
            .done(function() {
                view.model = model;
                model.loading = false;
            } )
            .done(function() {
                assert.notOk(model.loading);
            });
    });
});
