var Vue = require("vuejs");
var models = require("user/models");
var ApplicationView = require("user/vue-components/ApplicationView");
require("filters");

QUnit.module("user.app_view");
QUnit.test("rendering form", function (assert) {
    var done = assert.async();

    var model = new models.ApplicationListModel();
    var appView = new ApplicationView({
        data: function() { return { model: model }; }
    }).$mount();

    model.update().done(function() { Vue.nextTick(function() {
        assert.equal(appView.$el.children[0].tagName, 'DIV');
        assert.ok(appView.$el.children[0].classList.contains('row'));

        assert.equal(
            appView.$el.querySelector('.box-title').innerHTML,
            model.appList[0].appData.image.ui_name
        );

        // Simulate application starting
        model.appList[0].status = 'STARTING';

        assert.equal(
            appView.$el.querySelector('.box-title').innerHTML,
            model.appList[0].appData.image.ui_name
        );
        assert.equal(
            appView.$el.querySelector('#app-description').innerHTML,
            model.appList[0].appData.image.description
        );

        done();
    })});
});

QUnit.test("rendering iframe", function (assert) {
    var done = assert.async();

    var model = new models.ApplicationListModel();
    var appView = new ApplicationView({
        data: function() { return { model: model }; }
    }).$mount();

    model.update().done(function() {
        // Simulate application running
        model.appList[0].status = 'RUNNING';
        model.appList[0].appData.container = {};
        model.appList[0].appData.container.url_id = 'https://127.0.0.1:1234/';

        Vue.nextTick(function() {
            assert.equal(appView.$el.children[0].tagName, 'IFRAME');

            // Render form again by selecting the other application which is stopped
            model.selectedIndex = 1;

            Vue.nextTick(function() {
            console.log(model.appList[1].ui_name)
                assert.equal(
                    appView.$el.querySelector('.box-title').innerHTML,
                    model.appList[1].appData.image.ui_name
                );

                done();
            });
        });
    });
});
