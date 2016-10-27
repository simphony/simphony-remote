define([
    "jquery",
    "bootstrap",   // needed for modal operations.
    "utils",
    "jsapi/v1/resources"
], function ($, bootstrap, utils, resources) {
    "use strict";
    var base_url = window.apidata.base_url;

    $('#create-new-policy-dialog').on('show.bs.modal', function () {
        var dialog = $(this);
        $(dialog).find(".alert").hide();
        
        var ok_callback = function () {
            var rep = {
                user_name: $.trim($("#user_name").val()),
                image_name: $.trim($("#image_name").val()),
                allow_home: $("#allow_home").prop("checked"),
                volume_source: $.trim($("#volume_source").val()),
                volume_target: $.trim($("#volume_target").val()),
                volume_readonly: $("#volume_readonly").prop("checked")
            };

            $(dialog).find(".alert").hide();
            
            if (rep.image_name.length === 0) {
                $(dialog).find("#image_name_alert")
                    .text("Image name cannot be empty")
                    .show();
                return;
            }
            if (rep.volume_source.length !== 0 && rep.volume_source[0] !== '/') {
                $(dialog).find("#volume_source_alert")
                    .text("Must be an absolute path or empty")
                    .show();
                return;
            }
            
            if (rep.volume_target.length !== 0 && rep.volume_target[0] !== '/') {
                $(dialog).find("#volume_target_alert")
                    .text("Must be an absolute path or empty")
                    .show();
                return;
            }
                
            if (rep.volume_source.length === 0 && rep.volume_target.length !== 0) {
                $(dialog).find("#volume_source_alert")
                    .text("Must not be empty if target is defined")
                    .show();
                return;
            }
            
            if (rep.volume_source.length !== 0 && rep.volume_target.length === 0) {
                $(dialog).find("#volume_target_alert")
                    .text("Must not be empty if source is defined")
                    .show();
                return;
            }
            
            dialog.modal('hide');
            
            resources.Policies.create(rep)
                .done(function() { window.location.reload(); })
                .fail(utils.ajax_error_dialog);
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

    $('#create-new-policy-dialog').on('shown.bs.modal', function () {
        $("#image_name").focus();
    });

    $('#action-dialog').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget);
        var id = button.data('value');
        var name = button.data('name');
        var dialog = $(this);
        utils.config_dialog(
            dialog,
            'Remove policy ' + name + "?",
            "Do you want to remove policy " + name + "? ",
            function() {
                resources.Policies.delete(id)
                   .done(function() { window.location.reload(); })
                    .fail(utils.ajax_error_dialog);
            }
        );
    });
});
