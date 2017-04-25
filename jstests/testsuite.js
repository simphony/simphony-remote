(function () {
    require.config({
        baseUrl: "../remoteappmanager/static/js/",
        paths: {
          components: '../components',
          jquery: '../components/jquery/jquery.min',
          bootstrap: '../components/bootstrap/js/bootstrap.min',
          moment: "../components/moment/moment",
          "jsapi/v1/resources": "../../../jstests/tests/home/mock_jsapi",
          handlebars: "../components/handlebars/handlebars.amd.min",
          underscore: "../components/underscore/underscore-min",
          vue: "../components/vue/dist/vue"
        },
        shim: {
          bootstrap: {
            deps: ["jquery"],
            exports: "bootstrap"
          }
        }
    });

    require([
        "home/init",
        "tests/home/test_configurables.js",
        "tests/home/test_models.js",
        "tests/home/test_views.js",
        "tests/test_utils.js",
        "tests/test_analytics.js"
        ], function(init) {
            window.apidata = {
                base_url: "/",
                prefix: "/"
            };
            init.handlebars();

            QUnit.load();
            QUnit.start();
        });
}());

