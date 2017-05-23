var Vue = require("vuejs");
var ApplicationListModel = require("user/ApplicationListModel");
var ApplicationLabel = require("user/vue-components/ApplicationLabel");
var $ = require("jquery");
require("filters");

QUnit.module("user.app_label");
QUnit.test("application name", function(assert) {
  var done = assert.async();

  var model = new ApplicationListModel();
  var appLabel = new ApplicationLabel({
    data: function() { return { model: model }; }
  }).$mount();

  model.update().done(function() {
    Vue.nextTick(function() {
      assert.equal(
        appLabel.$el.querySelector('li > a > span').innerHTML,
        model.appList[0].appData.image.ui_name
      );

      // Simulate changing currentApp
      model.selectedIndex = 1;

      Vue.nextTick(function() {
        assert.equal(
          appLabel.$el.querySelector('li > a > span').innerHTML,
          model.appList[1].appData.image.ui_name
        );

        done();
      });
    })
  });
});

QUnit.test("rendering stop button", function (assert) {
  var done = assert.async();

  var model = new ApplicationListModel();
  var appLabel = new ApplicationLabel({
    data: function() { return { model: model }; }
  }).$mount();

  model.update().done(function() {
    // Simulate application stopped
    model.appList[0].status = 'STOPPED';

    Vue.nextTick(function() {
      assert.equal(
        appLabel.$el.querySelector('li > a > span').innerHTML,
        model.appList[0].appData.image.ui_name
      );

      // Test stop button disabled
      assert.ok(
        appLabel.$el.querySelector('#stop-button').classList.contains('disabled')
      );

      // Simulate application running
      model.appList[0].status = 'RUNNING';

      // Test stop button enabled
      Vue.nextTick(function() {
        assert.notOk(
          appLabel.$el.querySelector('#stop-button').classList.contains('disabled')
        );

        done();
      });
    })
  });
});
