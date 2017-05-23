var Vue = require("vuejs");
var ErrorDialog = require("vue/ErrorDialog");

QUnit.module("ErrorDialog");
QUnit.test("rendering errors one by one", function (assert) {
  var done = assert.async();

  var errorReceiver = [];
  var errorDialog = new ErrorDialog({
    data: function() { return { errorList: errorReceiver }; }
  }).$mount();

  Vue.nextTick(function() {
    // Error dialog not rendered (No error to show)
    assert.notEqual(errorDialog.$el.nodeType, Node.ELEMENT_NODE);

    errorReceiver.push({title: "Oups"});
    errorReceiver.push({code: 502});
    errorReceiver.push({title: "Oups", message: "Something happened..."});

    Vue.nextTick(function() {
      assert.equal(
        errorDialog.$el.textContent,
        "Oups  unknown error Cancel Ok"
      );

      errorDialog.okCallback(); // Simulate click ok
      Vue.nextTick(function() {
        assert.equal(
          errorDialog.$el.textContent,
          "Error Code: 502 unknown error Cancel Ok"
        );

        errorDialog.okCallback(); // Simulate click ok
        Vue.nextTick(function() {
          assert.equal(
            errorDialog.$el.textContent,
            "Oups  Something happened... Cancel Ok"
          );

          errorDialog.okCallback(); // Simulate click ok
          Vue.nextTick(function() {
            // Error dialog not rendered (No error to show)
            assert.notEqual(errorDialog.$el.nodeType, Node.ELEMENT_NODE);

            done();
          });
        });
      });
    });
  });
});

QUnit.test("rendering errors one by one", function (assert) {
  var done = assert.async();

  var errorReceiver = [];
  var errorDialog = new ErrorDialog({
    data: function() { return { errorList: errorReceiver }; }
  }).$mount();

  Vue.nextTick(function() {
    errorReceiver.push({title: "Oups"});
    errorReceiver.push({code: 502});
    errorReceiver.push({title: "Oups", message: "Something happened..."});

    Vue.nextTick(function() {
      assert.equal(
        errorDialog.$el.textContent,
        "Oups  unknown error Cancel Ok"
      );

      errorDialog.closeCallback(); // Simulate click close
      Vue.nextTick(function() {
        // Error dialog not rendered (Error list empty)
        assert.notEqual(errorDialog.$el.nodeType, Node.ELEMENT_NODE);

        done();
      });
    });
  });
});
