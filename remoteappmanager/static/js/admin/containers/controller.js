define([
    "jquery",
    "bootstrap",   // unused by module, but needed for binding modal dialog
    "admin/adminapi",
    "utils"
], function ($, bootstrap, adminapi, utils) {
    "use strict";
    var base_url = window.apidata.base_url;
    var appapi = new adminapi.AdminAPI(base_url);
    
    $('#action-dialog').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget);
        var url_id = button.data('value');
        var modal = $(this);
        utils.show_modal_dialog(
            modal,
            'Stop ' + url_id + "?",
            "Do you want to stop the container " + url_id + "? " +
            "This will stop the user session in that container.",
            function () {
                appapi.stop_container(url_id, {
                    success: function () {
                        window.location.reload();
                    },
                    error: utils.ajax_error_dialog
                });
            }
        );
    });
});
