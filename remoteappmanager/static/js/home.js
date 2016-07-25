// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.

require(["jquery", "jhapi", "remoteappapi"], 
        function($, JHAPI, RemoteAppAPI) {
    "use strict";
    
    var base_url = window.apidata.base_url;
    var user = window.apidata.user;
    var api = new JHAPI(base_url);
    var appapi = new RemoteAppAPI(base_url);
    
    $("#stop").click(function () {
        api.stop_server(user, {
            success: function () {
                $("#stop").hide();
            }
        });
    });
    
    $(".start-button").click(function () {
        var id = this.id;
        appapi.start_application(id, {
                success: function () {
                    window.location.reload()
                }
            });
    });

    $(".stop-button").click(function () {
        var id = this.id;
        appapi.stop_application(id, {
            success: function () {
                window.location.reload()
            }
        });
    });

});
