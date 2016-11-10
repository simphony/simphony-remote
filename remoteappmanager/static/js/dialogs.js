define([
    'jquery'
], function ($) {
    "use strict";

    var ajax_error_msg = function (jqXHR) {
        // Return a JSON error message if there is one,
        // otherwise the basic HTTP status text.
        if (jqXHR.responseJSON && jqXHR.responseJSON.message) {
            return jqXHR.responseJSON.message;
        } else {
            return jqXHR.statusText;
        }
    };

    var log_ajax_error = function (jqXHR, status, error) {
        // log ajax failures with informative messages
        var msg = "API request failed (" + jqXHR.status + "): ";
        console.log(jqXHR);
        msg += ajax_error_msg(jqXHR);
        console.log(msg);
        return msg;
    };

    var ajax_error_dialog = function (jqXHR, status, error) {
        console.log("ajax dialog", arguments);
        var msg = log_ajax_error(jqXHR, status, error);
        var dialog = $("#error-dialog");
        dialog.find(".ajax-error").text(msg);
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
        ajax_error_dialog : ajax_error_dialog,
        config_dialog : config_dialog
    };

}); 
