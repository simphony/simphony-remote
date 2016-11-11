define([
    "jquery",
    "bootstrap",   // needed for modal operations.
    "dialogs",
    "jsapi/v1/resources"
], function ($, bootstrap, dialogs, resources) {
    "use strict";

    $('#create-new-policy-dialog').on('show.bs.modal', function () {
        var dialog = $(this);
        $(dialog).find(".alert").hide();
        
        var ok_callback = function () {
            var user_name = $.trim($("#user_name").val());
            var image_name = $.trim($("#image_name").val());
            var allow_home = $("#allow_home").prop("checked");
            var volume_source = $.trim($("#volume_source").val());
            var volume_target = $.trim($("#volume_target").val());
            var volume_readonly = $("#volume_readonly").prop("checked");
           
            $(dialog).find(".alert").hide();
            
            if (image_name.length === 0) {
                $(dialog).find("#image_name_alert")
                    .text("Image name cannot be empty")
                    .show();
                return;
            }
            if (volume_source.length !== 0 && volume_source[0] !== '/') {
                $(dialog).find("#volume_source_alert")
                    .text("Must be an absolute path or empty")
                    .show();
                return;
            }
            
            if (volume_target.length !== 0 && volume_target[0] !== '/') {
                $(dialog).find("#volume_target_alert")
                    .text("Must be an absolute path or empty")
                    .show();
                return;
            }
                
            if (volume_source.length === 0 && volume_target.length !== 0) {
                $(dialog).find("#volume_source_alert")
                    .text("Must not be empty if target is defined")
                    .show();
                return;
            }
            
            if (volume_source.length !== 0 && volume_target.length === 0) {
                $(dialog).find("#volume_target_alert")
                    .text("Must not be empty if source is defined")
                    .show();
                return;
            }
            
            var rep = {
                user_name: user_name,
                image_name: image_name,
                allow_home: allow_home
            };
            
            if (volume_source.length !== 0 && volume_target.length !== 0) {
                var volume_mode;
                if (volume_readonly) {
                    volume_mode = "ro";
                } else {
                    volume_mode = "rw";
                }
                rep.volume = volume_source+":"+volume_target+":"+volume_mode;
            }

            dialog.modal('hide');
            
            resources.Accounting.create(rep)
                .done(function() { window.location.reload(); })
                .fail(dialogs.webapi_error_dialog);
        };

        var cancel_callback = function () {
            dialog.modal('hide');
        };

        $(dialog).find("form").on('submit', function(e) {
            e.preventDefault();
            ok_callback();
        });

        dialogs.config_dialog(
            dialog,
            null,
            null,
            ok_callback,
            cancel_callback
        );
    });

    $('#create-new-policy-dialog').on('shown.bs.modal', function () {
        $("#image_name").focus();
    });

    $('#action-dialog').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget);
        var id = button.data('value');
        var name = button.data('name');
        var dialog = $(this);
        dialogs.config_dialog(
            dialog,
            'Remove policy ' + name + "?",
            "Do you want to remove policy " + name + "? ",
            function() {
                resources.Accounting.delete(id)
                   .done(function() { window.location.reload(); })
                    .fail(dialogs.webapi_error_dialog);
            }
        );
    });
});
