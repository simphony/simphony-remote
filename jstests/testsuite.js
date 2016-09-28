(function () {
    require.config({
        baseUrl: "../remoteappmanager/static/js/",
        paths: {
          components: '../components',
          jquery: '../components/jquery/jquery.min',
          bootstrap: '../components/bootstrap/js/bootstrap.min',
          moment: "../components/moment/moment",
        },
        shim: {
          bootstrap: {
            deps: ["jquery"],
            exports: "bootstrap"
          },
        }
    });

	require([
        "tests/home/test_configurables.js",
        "tests/home/test_models.js",
        "tests/home/test_views.js",
        "tests/test_remoteappapi.js",
        "tests/test_utils.js"
        ], function() {
            window.apidata = {
                base_url: "/",
                prefix: "/"
            };
            QUnit.load();
            QUnit.start();
	    });
}());

