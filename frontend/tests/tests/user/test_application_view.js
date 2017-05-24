var Vue = require("vuejs");
var ApplicationListModel = require("user/ApplicationListModel");
var ApplicationView = require("user/vue-components/ApplicationView");
require("filters");

QUnit.module("user.app_view");
QUnit.test("rendering form", function (assert) {
  var done = assert.async();

  var model = new ApplicationListModel();
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
  });});
});

QUnit.test("rendering iframe", function (assert) {
  var done = assert.async();

  var model = new ApplicationListModel();
  var appView = new ApplicationView({
    data: function() { return { model: model }; }
  }).$mount();

  model.update().done(function() {
    // Switch to a running application
    model.selectedIndex = 1;

    Vue.nextTick(function() {
      assert.equal(appView.$el.children[0].tagName, 'IFRAME');
      assert.equal(appView.$el.children[0].getAttribute('src'), '/user/lambda/containers/654321/');

      // Render form again by selecting the other application which is stopped
      model.selectedIndex = 0;

      Vue.nextTick(function() {
        assert.equal(
          appView.$el.querySelector('.box-title').innerHTML,
          model.appList[0].appData.image.ui_name
        );

        done();
      });
    });
  });
});
