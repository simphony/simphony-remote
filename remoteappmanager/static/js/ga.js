define(function (require) {
    var module;

    if (window.apidata.google_analytics !== undefined) {
        window.GoogleAnalyticsObject = "ga";
        window.ga = function () { 
            (window.ga.q = window.ga.q || []).push(arguments); 
        };
        window.ga.l = 1 * new Date();
        module = function () { window.ga.apply(this, arguments); };
        require(["//www.google-analytics.com/analytics.js"]);
        window.ga('create', window.apidata.google_analytics.tracking_id, 'auto');
    } else {
        window.ga = function () {};
        module = function () { window.ga.apply(this, arguments); };
    }
    

    return module;
});
