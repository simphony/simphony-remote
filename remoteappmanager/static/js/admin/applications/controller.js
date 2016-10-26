require([
    "jquery",
    "bootstrap",   // needed for modal operations.
    "utils",
    "jsapi/v1/resources"
], function ($, bootstrap, utils, resources) {
    "use strict";
    var base_url = window.apidata.base_url;

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
            resources.Application.create({ image_name: image_name })
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
                resources.Application.delete(id)
                    .done(function() { window.location.reload(); })
                    .fail(utils.ajax_error_dialog);
            }
        );
    });
});
