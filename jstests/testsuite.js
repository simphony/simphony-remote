(function () {
    require.config({
        baseUrl: "../remoteappmanager/static/js/",
        paths: {
          jstests: '../../../jstests/',
          components: '../components',
          jquery: '../components/jquery/jquery.min',
          bootstrap: '../components/bootstrap/js/bootstrap.min',
          moment: "../components/moment/moment",
          "jsapi/v1/resources": "../../../jstests/tests/home/mock_jsapi",
          underscore: "../components/underscore/underscore-min"
        },
        shim: {
          bootstrap: {
            deps: ["jquery"],
            exports: "bootstrap"
          }
        }
    });

    require([
        "tests/home/test_configurables.js",
        "tests/home/test_models.js",
        "tests/home/test_application_list_view.js",
        "tests/home/test_application_view.js",
        "tests/vue/components/test_DataTable.js",
        "tests/vue/components/test_ConfirmDialog.js",
        "tests/test_utils.js",
        "tests/test_analytics.js"
        ], function() {
            window.apidata = {
                base_url: "/",
                prefix: "/"
            };

            QUnit.load();
            QUnit.start();
        });
}());

