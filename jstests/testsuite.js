(function () {
    blanket.options("autoStart", false);
    blanket.options("existingRequireJS", true);
    
    require.config({
        baseUrl: "../remoteappmanager/static/js/",
        paths: {
          components: '../components',
          jquery: '../components/jquery/jquery.min',
          bootstrap: '../components/bootstrap/js/bootstrap.min',
          moment: "../components/moment/moment",
        },
        onNodeCreated: function (node) {
            node.setAttribute("data-cover", "");
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
        ], function() {
            window.apidata = {
                base_url: "/",
                prefix: "/"
            };
            QUnit.load();
            QUnit.start();
	    });
}());

