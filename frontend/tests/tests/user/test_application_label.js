let Vue = require("vuejs");
let ApplicationListModel = require("user/ApplicationListModel");
let ApplicationLabel = require("user/vue-components/ApplicationLabel");
require("filters");

let model, appLabel;

QUnit.module("user.app_label", {
  beforeEach: function(assert) {
    let done = assert.async();

    model = new ApplicationListModel();
    appLabel = new ApplicationLabel({
      data: function() { return { model: model }; }
    }).$mount();

    model.update().done(function() {
      Vue.nextTick(function() {done();});
    });
  }
});

QUnit.test("application name", function(assert) {
  let done = assert.async();

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
});

QUnit.test("rendering stop button", function (assert) {
  let done = assert.async();

  assert.equal(
    appLabel.$el.querySelector('li > a > span').innerHTML,
    model.appList[0].appData.image.ui_name
  );

  // Test stop button disabled
  assert.ok(
    appLabel.$el.querySelector('#stop-button').classList.contains('disabled')
  );

  // Select running application
  model.selectedIndex = 1;

  // Test stop button enabled
  Vue.nextTick(function() {
    assert.notOk(
      appLabel.$el.querySelector('#stop-button').classList.contains('disabled')
    );

    done();
  });
});

QUnit.test("rendering share button", function (assert) {
  let done = assert.async();

  // Test share button disabled
  assert.ok(
    appLabel.$el.querySelector('#share-button').classList.contains('disabled')
  );

  // Select running application
  model.selectedIndex = 1;

  // Test share button disabled (Because clipboard save is not supported in test environment)
  Vue.nextTick(function() {
    assert.ok(
      appLabel.$el.querySelector('#share-button').classList.contains('disabled')
    );

    done();
  });
});
