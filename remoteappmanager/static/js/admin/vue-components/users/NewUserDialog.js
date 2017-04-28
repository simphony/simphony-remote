define([
  "jquery",
  "components/vue/dist/vue",
  "jsapi/v1/resources"
], function($, Vue, resources) {
  "use strict";

  return {
    template: `
        <modal>
          <div class="modal-header"><h4>Create New User</h4></div>
          <div class="modal-body">
            <vue-form :state="formstate" v-model="formstate" @submit.prevent="createNewUser">
              <validate auto-label class="form-group required-field" :class="fieldClassName(formstate.name)">
                <label class="control-label">User Name</label>
                <input type="text" name="name" class="form-control" required v-model="model.name">

                <field-messages name="name" show="$touched || $submitted">
                  <span class="help-block" slot="required">User Name cannot be empty</span>
                </field-messages>
              </validate>

              <div class="modal-footer">
                <button type="button" class="btn btn-default" @click="close()">Cancel</button>
                <button class="btn btn-primary" type="submit" :disabled="formstate.$invalid">Submit</button>
              </div>
            </vue-form> 
          </div>
      </modal>`,
    props: ['show'],

    data: function () {
      return {
        formstate: {},
        model: {
          name: ''
        }
      };
    },
    methods: {
      close: function () {
        this.$emit('closed');
      },
      fieldClassName: function (field) {
        if (!field) {
          return '';
        }
        if ((field.$touched || field.$submitted) && field.$invalid) {
          return 'has-error';
        } else {
          return '';
        }
      },
      createNewUser: function () {
        if (!this.formstate.$valid) {
          return;
        }
        var user_name = $.trim(this.model.name);
        resources.User.create({name: user_name})
          .done((
            function () {
              this.$emit('created');
            }).bind(this)
          )
          .fail(
            (function () {
              this.$emit("closed");
            }).bind(this)
          );
      },
      reset: function () {
        Object.assign(this.$data, this.$options.data());
      }
    },
    watch: {
      "show": function (value) {
        if (value) {
          this.reset();
        }
      }
    }
  };
});
