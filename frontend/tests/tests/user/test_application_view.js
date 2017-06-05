let $ = require("jquery");
let Vue = require("vuejs");
let ApplicationListModel = require("user/ApplicationListModel");
let ApplicationView = require("user/vue-components/ApplicationView");
require("filters");

let model, appView;

QUnit.module("user.app_view", {
  beforeEach: function(assert) {
    let done = assert.async();

    model = new ApplicationListModel();
    appView = new ApplicationView({
      data: function() { return { model: model }; }
    }).$mount();

    model.update().done(function() {
      Vue.nextTick(function() {done();});
    });
  }
});

QUnit.test("rendering title and description", function (assert) {
  let done = assert.async();
  assert.equal(appView.$el.children[0].tagName, 'DIV');
  assert.ok(appView.$el.children[0].classList.contains('row'));

  assert.equal(
    appView.$el.querySelector('.box-title').innerHTML,
    model.appList[0].appData.image.ui_name
  );

  assert.equal(
    appView.$el.querySelector('#app-description').innerHTML,
    model.appList[0].appData.image.description
  );

  // Select other application
  model.selectedIndex = 2;

  Vue.nextTick(function() {
    assert.equal(
      appView.$el.querySelector('.box-title').innerHTML,
      model.appList[2].appData.image.ui_name
    );

    assert.equal(
      appView.$el.querySelector('#app-description').innerHTML,
      model.appList[2].appData.image.description
    );

    done();
  });
});

QUnit.test("rendering policy", function (assert) {
  let done = assert.async();

  assert.equal(
    appView.$el.querySelector('.policy').children[0].innerHTML.trim(),
    'Workspace accessible'
  );

  assert.equal(
    appView.$el.querySelector('.policy').children[1].innerHTML.trim(),
    'No volumes mounted'
  );

  // Select other application
  model.selectedIndex = 2;

  Vue.nextTick(function() {
    assert.equal(
      appView.$el.querySelector('.policy').children[0].innerHTML.trim(),
      'Workspace not accessible'
    );

    assert.notEqual(
      appView.$el.querySelector('.policy').children[1].innerHTML.indexOf('Volume mounted: foo'),
      -1
    );

    assert.notEqual(
      appView.$el.querySelector('.policy').children[1].innerHTML.indexOf(' bar (baz)'),
      -1
    );

    done();
  });
});

QUnit.test("rendering configurables", function (assert) {
  let done = assert.async();

  assert.notEqual(
    appView.$el.querySelector('.configuration').children[0].innerHTML.trim(),
    'No configurable options for this image'
  );

  // Select other application
  model.selectedIndex = 2;

  Vue.nextTick(function() {
    assert.equal(
      appView.$el.querySelector('.configuration').children[0].innerHTML.trim(),
      'No configurable options for this image'
    );

    done();
  });
});

QUnit.test("rendering start button", function (assert) {
  let done = assert.async();

  assert.equal(
    appView.$el.querySelector('.start-button').innerHTML.trim(),
    'Start'
  );

  assert.notOk(
    appView.$el.querySelector('.start-button').disabled
  );

  assert.notOk(
    appView.$el.querySelector('.configuration > fieldset').disabled
  );

  // Simulate application starting
  model.appList[0].status = 'STARTING';

  Vue.nextTick(function() {
    assert.equal(
      appView.$el.querySelector('.start-button').innerHTML.trim(),
      'Starting'
    );

    assert.ok(
      appView.$el.querySelector('.start-button').disabled
    );

    // Simulate application stopping
    model.appList[0].status = 'STOPPING';

    Vue.nextTick(function() {
      assert.equal(
        appView.$el.querySelector('.start-button').innerHTML.trim(),
        'Stopping'
      );

      assert.ok(
        appView.$el.querySelector('.start-button').disabled
      );

      done();
    });
  });
});

QUnit.test("start method", function (assert) {
  let done = assert.async();

  let startCalled = false;
  // Mock model.startApplication
  model.startApplication = function() {
    let startPromise = $.Deferred();
    startCalled = true;
    return startPromise.resolve();
  };

  // Select stopped application
  model.selectedIndex = 0;

  Vue.nextTick(function() {
    // model.startApplication should be called
    appView.startApplication().then(function() {
      assert.ok(startCalled);

      // Select running application
      model.selectedIndex = 1;
      startCalled = false;

      Vue.nextTick(function() {
        // model.startApplication shouldn't be called
        appView.startApplication().then(function() {
          assert.notOk(startCalled);
          done();
        });
      });
    });
  });
});

QUnit.test("rendering iframe", function (assert) {
  let done = assert.async();
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
