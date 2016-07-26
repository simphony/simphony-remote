// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.

require(["jquery", "jhapi", "utils", "remoteappapi"],
        function($, JHAPI, utils, RemoteAppAPI) {
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
        $(this).find(".fa-spinner").show();

        appapi.start_application(id, {
                statusCode: {
                    201: function (data, textStatus, request) {
                        var location = request.getResponseHeader('Location');
                        var url = utils.parse_url(location);
                        var arr = url.pathname.replace(/\/$/, "").split('/');
                        var id = arr[arr.length-1];
                        
                        window.location = utils.url_path_join(
                            base_url,
                            "containers",
                            id
                        )
                    }
                }
            });
        }
    );
            
    $(".view-button").click(function () {
        var id = this.id;
        window.location = utils.url_path_join(
            base_url,
            "containers",
            id)
        }
    );

    $(".stop-button").click(function () {
        var id = this.id;
        $(this).find(".fa-spinner").show();
        appapi.stop_application(id, {
            success: function () {
                window.location.reload()
            }
        });
    });

});
