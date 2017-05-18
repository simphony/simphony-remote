var Vue = require("vuejs");
var models = require("user/models");
var ApplicationListView = require("user/vue-components/ApplicationListView");
require("filters");

QUnit.module("user.app_list_view");
QUnit.test("rendering list", function (assert) {
    var done = assert.async();

    var model = new models.ApplicationListModel();
    var appListView = new ApplicationListView({
        data: function() { return { model: model }; }
    }).$mount();

    assert.ok(model.loading);
    assert.equal(
        appListView.$el.querySelector("#loading-spinner").style.display,
        ""
    );

    model.update().done(function() { Vue.nextTick(function() {
        assert.equal(
            appListView.$el.querySelector("#no-app-msg").style.display,
            "none"
        );
        assert.equal(
            appListView.$el.querySelector("#loading-spinner").style.display,
            "none"
        );
        assert.equal(
            appListView.$el.querySelector("#applistentries").children.length,
            model.appList.length
        );

        done();
    })});
});

QUnit.test("rendering nothing in the list", function (assert) {
    var done = assert.async();

    var model = new models.ApplicationListModel();
    var appListView = new ApplicationListView({
        data: function() { return { model: model }; }
    }).$mount();

    model.loading = false;

    Vue.nextTick(function() {
        assert.equal(
            appListView.$el.querySelector("#no-app-msg").style.display,
            ""
        );
        assert.equal(
            appListView.$el.querySelector("#loading-spinner").style.display,
            "none"
        );
        assert.equal(
            appListView.$el.querySelector("#applistentries").children.length,
            0
        );

        done();
    });
});

QUnit.test("search form", function (assert) {
    var done = assert.async();

    var model = new models.ApplicationListModel();
    var appListView = new ApplicationListView({
        data: function() { return { model: model }; }
    }).$mount();

    model.update().done(function() { Vue.nextTick(function() {
        assert.notEqual(appListView.visibleList.length, 0);

        appListView.searchInput = "heho";

        Vue.nextTick(function() {
            assert.equal(appListView.visibleList.length, 0);
            assert.equal(
                appListView.$el.querySelector("input[name=q]").value,
                "heho"
            );

            done();
        })
    })});
});
