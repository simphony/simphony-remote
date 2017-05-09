define([
    "home/models",
    "home/views/application_list_view",
    "components/vue/dist/vue",
    "filters"
], function (models, application_list_view, Vue) {
    "use strict";

    QUnit.module("home.app_list_view");
    QUnit.test("rendering list", function (assert) {
        // assert.expect(3);
        var done = assert.async();

        var model = new models.ApplicationListModel();
        var app_list_view = new application_list_view.ApplicationListView({
            data: function() { return { model: model }; }
        }).$mount();

        assert.ok(model.loading);
        assert.equal(
            app_list_view.$el.querySelector("#loading-spinner").style.display,
            ""
        )

        model.update().done(function() {
            console.log(app_list_view.$el.querySelector("#loading-spinner").style.display)
            Vue.nextTick(function() {
                console.log("Calling nexttick")
                assert.equal(
                    app_list_view.$el.querySelector("#loading-spinner").style.display,
                    "none"
                )
                done();
            });
        });
    });
});
