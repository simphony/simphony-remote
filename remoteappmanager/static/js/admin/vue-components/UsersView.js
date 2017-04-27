define([
  "components/vue/dist/vue.min"
], function(Vue) {
  "use strict";

  return {
    template: `
<div class="row">
  <div class="col-md-12">
    <div class="box">
      <div class="box-header with-border">Users</div>
      <div class="box-body">
        <table id="datatable" class="display dataTable">
          <thead>
          <tr>
              <th>ID</th>
              <th>Username</th>
              <th>Actions</th>
          </tr>
          </thead>
          <tbody>
            <tr>
              <td>{{ u.id }}</td>
              <td>{{ u.name }}</td>
              <td><a href="{{ base_url }}users/{{ u.id }}/accounting/">Show</a></td>
              <td><button class="btn btn-danger"
                          data-value="{{ u.id }}"
                          data-name="{{ u.name }}"
                          data-toggle="modal"
                          data-target="#action-dialog">Remove</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</div>`,
    data: function () {
      return {};
    },
    mounted: function () {
    }
  };
});
