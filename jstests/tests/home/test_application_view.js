define([
    "home/models",
    "home/views/application_view",
    "components/vue/dist/vue",
    "vue/filters"
], function (models, application_view, Vue) {
    "use strict";

    QUnit.module("home.app_view");
    QUnit.test("rendering form", function (assert) {
        var done = assert.async();

        var model = new models.ApplicationListModel();
        var app_view = new application_view.ApplicationView({
            data: function() { return { model: model }; }
        }).$mount();

        model.update().done(function() { Vue.nextTick(function() {
            assert.equal(app_view.$el.children[0].tagName, 'DIV');
            assert.ok(app_view.$el.children[0].classList.contains('row'));

            assert.equal(
                app_view.$el.querySelector('.box-title').innerHTML,
                model.app_list[0].app_data.image.ui_name
            );

            // Simulate application starting
            model.app_list[0].status = 'STARTING';

            assert.equal(
                app_view.$el.querySelector('.box-title').innerHTML,
                model.app_list[0].app_data.image.ui_name
            );

            assert.equal(
                app_view.$el.querySelector('#app-description').innerHTML,
                model.app_list[0].app_data.image.description
            );

            done();
        })});
    });

    QUnit.test("rendering iframe", function (assert) {
        var done = assert.async();

        var model = new models.ApplicationListModel();
        var app_view = new application_view.ApplicationView({
            data: function() { return { model: model }; }
        }).$mount();

        model.update().done(function() {
            // Simulate application running
            model.app_list[0].status = 'RUNNING';
            model.app_list[0].app_data.container = {};
            model.app_list[0].app_data.container.url_id = 'https://127.0.0.1:1234/';

            Vue.nextTick(function() {
                assert.equal(app_view.$el.children[0].tagName, 'IFRAME');

                // Render form again by selecting the other application which is stopped
                model.selected_index = 1;

                Vue.nextTick(function() {
                console.log(model.app_list[1].ui_name)
                    assert.equal(
                        app_view.$el.querySelector('.box-title').innerHTML,
                        model.app_list[1].app_data.image.ui_name
                    );

                    done();
                });
            });
        });
    });
});
