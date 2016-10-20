define([
    "jquery",
    "admin/tabular/controller",
    "remoteappapi"
], function ($, tabular, RemoteAppAPI) {
    "use strict";
    var base_url = window.apidata.base_url;
    var appapi = new RemoteAppAPI(base_url);
    
    $("button").click(
        function() {
            var url_id = $(this).attr("data-value");
            appapi.stop_application(url_id, {
                success: function () {
                    window.location.reload();
                }});
    });
});
