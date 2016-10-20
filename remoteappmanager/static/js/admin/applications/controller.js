define([
    "jquery",
    "admin/adminapi"
], function ($, adminapi) {
    "use strict";
    var base_url = window.apidata.base_url;
    var appapi = new adminapi.AdminAPI(base_url);

    console.log($(".modal"));

    $('.modal').on('show.bs.modal', function (event) {
      var button = $(event.relatedTarget);
      var id = button.data('value');
      var name = button.data('name');
      var modal = $(this);
      modal.find('.modal-title').text('Remove ' + name + "?");
      modal.find('.modal-body').text(
          "Do you want to remove application " +
          name + 
          "? This will also remove the associated user policies."
      );
      modal.find('.modal-footer .primary').click(
          function() {
              appapi.remove_application(id, {
                  success: function () {
                      window.location.reload();
                  }});
        });
    });
});
