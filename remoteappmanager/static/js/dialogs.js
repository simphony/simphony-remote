define([
    'jquery'
], function ($) {
    "use strict";

    var webapi_error_dialog = function (error) {
        // Shows the error dialog with a webapi error.
        // The webapi error is an object with the following props:
        // - status : HTTP error status
        // - message: user-readable message from the server via the
        //            response payload. may be undefined.
        
        var msg = error.message;
        if (!msg) {
            msg = "Unknown error";
        }
        var dialog = $("#error-dialog");
        dialog.find(".ajax-error").text(msg + "<br>Status: " + error.status);
        dialog.modal();
    };

    var config_dialog = function(dialog_element, title, body, ok_callback, close_callback) {
        var modal = $(dialog_element);

        // Remove possible already existing handlers
        modal.find('.modal-footer .primary').off("click");
        modal.find('.modal-close').off("click");

        if (title !== null) {
            modal.find('.modal-title').text(title);
        }
        if (body !== null) {
            modal.find('.modal-body').text(body);
        }
        if (ok_callback !== null) {
            modal.find('.modal-footer .primary').click(ok_callback);
        }
        if (close_callback !== null) {
            modal.find('.modal-close').click(close_callback);
        }
    };

    return {
        webapi_error_dialog : webapi_error_dialog,
        config_dialog : config_dialog
    };

}); 
