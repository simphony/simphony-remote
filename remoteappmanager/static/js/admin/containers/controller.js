define([
    "jquery",
    "bootstrap",   // unused by module, but needed for binding modal dialog
    "utils",
    "jsapi/v1/resources"
], function ($, bootstrap, adminapi, utils, resources) {
    "use strict";
    var base_url = window.apidata.base_url;
    
    $('#action-dialog').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget);
        var url_id = button.data('value');
        var dialog = $(this);
        utils.config_dialog(
            dialog,
            'Stop ' + url_id + "?",
            "Do you want to stop the container " + url_id + "? " +
            "This will stop the user session in that container.",
            function () {
                resources.Container.delete(url_id,
                    function () { window.location.reload(); },
                    utils.ajax_error_dialog
                );
            }
        );
    });
});
