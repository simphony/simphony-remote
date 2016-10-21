define([
    "jquery",
    "bootstrap",   // needed for modal operations.
    "utils",
    "admin/adminapi"
], function ($, bootstrap, utils, adminapi) {
    "use strict";
    var base_url = window.apidata.base_url;
    var appapi = new adminapi.AdminAPI(base_url);

    $('#create-new-dialog').on('show.bs.modal', function () {
        var dialog = $(this);
        $(dialog).find(".alert").hide();
        
        var ok_callback = function () {
            var image_name = $.trim($("#image-name").val());
            if (image_name.length === 0) {
                $(dialog).find(".alert").show();
                return;
            }
            dialog.modal('hide');
            appapi.create_application(image_name, {
                success: function () {
                    window.location.reload();
                },
                error: utils.ajax_error_dialog
            });
        };
        
        var cancel_callback = function () {
            dialog.modal('hide');
        };
        
        $(dialog).find("form").on('submit', function(e) {
            e.preventDefault();
            ok_callback();
        });

        utils.config_dialog(
            dialog,
            null,
            null,
            ok_callback,
            cancel_callback
        );
    });
    
    $('#create-new-dialog').on('shown.bs.modal', function () {
        $("#image-name").focus();
    });
    
    $('#action-dialog').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget);
        var id = button.data('value');
        var name = button.data('name');
        var dialog = $(this);
        utils.config_dialog(
            dialog,
            'Remove ' + name + "?",
            "Do you want to remove application " + name + "? " +
            "This will also remove the associated user policies.",
            function() {
                appapi.remove_application(id, {
                    success: function () {
                      window.location.reload();
                    },
                    error: utils.ajax_error_dialog
                });
            }
        );
    });
});
