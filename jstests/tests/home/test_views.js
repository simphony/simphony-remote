define([
    "home/models",
    "home/views/application_list_view",
    "components/vue/dist/vue",
    "filters"
], function (models, application_list_view, Vue) {
    "use strict";

    QUnit.module("home.app_list_view");
    QUnit.test("rendering list", function (assert) {
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

        model.update().done(function() { Vue.nextTick(function() {
            assert.equal(
                app_list_view.$el.querySelector("#loading-spinner").style.display,
                "none"
            )

            assert.equal(
                app_list_view.$el.querySelector("#applistentries").children.length,
                model.app_list.length + 2
            )

            // Clear the model's application list
            model.app_list = [];

            Vue.nextTick(function() {
                assert.equal(
                    app_list_view.$el.querySelector("#applistentries > li > a").style.display,
                    ""
                )

                assert.equal(
                    app_list_view.$el.querySelector("#applistentries").children.length,
                    2
                )

                done();
            });
        })});
    });

    QUnit.test("search form", function (assert) {
        var done = assert.async();

        var model = new models.ApplicationListModel();
        var app_list_view = new application_list_view.ApplicationListView({
            data: function() { return { model: model }; }
        }).$mount();

        model.update().done(function() { Vue.nextTick(function() {
            assert.notEqual(app_list_view.visible_list.length, 0);

            app_list_view.search_input = "heho"

            Vue.nextTick(function() {
                assert.equal(app_list_view.visible_list.length, 0);

                assert.equal(
                    app_list_view.$el.querySelector("input[name=q]").value,
                    "heho"
                );

                done();
            })
        })});
    });
});
