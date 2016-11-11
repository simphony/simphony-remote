require([
    "jquery",
    "bootstrap",   // unused by module, but needed for binding modal dialog
    "dialogs",
    "jsapi/v1/resources"
], function ($, bootstrap, dialogs, resources) {
    "use strict";
    
    $('#action-dialog').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget);
        var url_id = button.data('value');
        var dialog = $(this);
        dialogs.config_dialog(
            dialog,
            'Stop ' + url_id + "?",
            "Do you want to stop the container " + url_id + "? " +
            "This will stop the user session in that container.",
            function () {
                resources.Container.delete(url_id)
                    .done(function () { window.location.reload(); })
                    .fail(dialogs.webapi_error_dialog);
            }
        );
    });
});
