define([
    "jquery",
    "dialogs",
    "jsapi/v1/resources"
], function ($, dialogs, resources) {
    "use strict";

    $('#create-new-dialog').on('shown.bs.modal', function () {
        $("#user-name").focus();
    });

    $('#action-dialog').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget);
        var id = button.data('value');
        var name = button.data('name');
        var dialog = $(this);
        dialogs.config_dialog(
            dialog,
            'Remove ' + name + "?",
            "Do you want to remove user " + name + "? " +
            "This will also remove the associated policies.",
            function() {
                resources.User.delete(id)
                    .done(function() { window.location.reload(); })
                    .fail(dialogs.webapi_error_dialog);
            }
        );
    });
});
