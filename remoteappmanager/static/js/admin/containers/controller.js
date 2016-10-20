define([
    "jquery",
    "bootstrap",   // unused by module, but needed for binding modal dialog
    "admin/adminapi"
], function ($, bootstrap, adminapi) {
    "use strict";
    var base_url = window.apidata.base_url;
    var appapi = new adminapi.AdminAPI(base_url);
    
    $('.modal').on('show.bs.modal', function (event) {
      var button = $(event.relatedTarget);
      var url_id = button.data('value');
      var modal = $(this);
      modal.find('.modal-title').text('Stop ' + url_id + "?");
      modal.find('.modal-body').text(
          "Do you want to stop the container " +
          url_id + 
          "? This will stop the user session in that container."
      );
      modal.find('.modal-footer .primary').click(
          function() {
              appapi.stop_application(url_id, {
                  success: function () {
                      window.location.reload();
                  }});
        });
    });
});
