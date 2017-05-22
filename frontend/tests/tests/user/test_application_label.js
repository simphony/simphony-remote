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

QUnit.test("display stopping error", function(assert) {
  var done = assert.async();

  var model = new ApplicationListModel();
  var appLabel = new ApplicationLabel({
    data: function() { return { model: model }; }
  }).$mount();

  // Change model.stopApplication so that it returns an error
  model.stopApplication = function(index) {
    var stopPromise = new $.Deferred();
    stopPromise.reject({ message: 'Oups', code: '456' });
    return stopPromise;
  };

  model.update().done(function() {
    // Simulate app running
    model.appList[0].status = 'RUNNING';

    Vue.nextTick(function() {
      // Error dialog is not rendered
      assert.equal(appLabel.$el.children[0].tagName, 'LI');

      // This will call model.stopApplication. Should fail and display a dialog error
      appLabel.stopApplication();

      Vue.nextTick(function() {
        // Error dialog is rendered
        assert.equal(appLabel.$el.children[0].tagName, 'DIV');
        assert.ok(appLabel.$el.children[0].classList.contains('modal'));

        assert.equal(
          appLabel.$el.querySelector('#error-msg > strong').innerHTML,
          'Code: 456'
        );
        assert.equal(
          appLabel.$el.querySelector('#error-msg > span').innerHTML,
          'Oups'
        );

        done();
      });
    })
  });
});
