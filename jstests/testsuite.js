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

