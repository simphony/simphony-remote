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
		"tests/test_remoteappapi.js",
		"tests/test_utils.js"
        ], function() {
            QUnit.load();
            QUnit.start();
	    });
}());

