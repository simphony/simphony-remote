define([
  "jquery",
  "components/vue/dist/vue",
  "jsapi/v1/resources"
], function($, Vue, resources) {
  "use strict";

  return {
    template: `
        <modal>
          <div class="modal-header"><h4>Create New Policy</h4></div>
          <div class="modal-body">
            <vue-form :state="formstate" v-model="formstate" @submit.prevent="createNewAccounting">
              <validate auto-label class="form-group required-field" :class="fieldClassName(formstate.image_name)">
                <label class="control-label">Image Name</label>
                <input type="text" name="image_name" class="form-control" required v-model="model.image_name">

                <field-messages name="image_name" show="$touched || $submitted">
                  <span class="help-block" slot="required">Image Name cannot be empty</span>
                </field-messages>
              </validate>
              
              <div class="form-group">
                  <label>
                    <input type="checkbox" id="allow_home" v-model="model.allow_home"/> Mount home as Workspace
                  </label>
              </div>
              
              <validate auto-label class="form-group" :custom="{validatePath: validatePath}" :class="fieldClassName(formstate.volume_source)">
                <div class="form-group">
                    <label for="volume_source">Volume Source</label>
                    <input type="text" class="form-control" name="volume_source" placeholder="/local/path" v-model="model.volume_source"/>
                </div>
                <field-messages name="volume_source">
                  <span class="help-block" slot="validatePath">Volume Source must be empty or an absolute path</span>
                  <span class="help-block" slot="volumesInconsistent">Both Volume Source and Target must be defined</span>
                </field-messages>
              </validate>
              
              <validate auto-label :custom="{validatePath: validatePath}" class="form-group" :class="fieldClassName(formstate.volume_target)">
                <div class="form-group">
                    <label for="volume_target">Volume Target</label>
                    <input type="text" class="form-control" name="volume_target" placeholder="/container/path" v-model="model.volume_target"/>
                </div>
                <field-messages name="volume_target">
                  <span class="help-block" slot="validatePath">Volume Target must be empty or an absolute path</span>
                  <span class="help-block" slot="volumesInconsistent">Both Volume Source and Target must be defined</span>
                </field-messages>
              </validate>
              
              <div class="form-group">
                <label>
                  <input type="checkbox" name="volume_readonly" v-model="model.volume_readonly" /> Mount volume readonly
                </label>
              </div>

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
          image_name: '',
          allow_home: false,
          volume_source: '',
          volume_target: '',
          volume_readonly: false,
          volume_source_target: []
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
        if ((field.$dirty || field.$submitted) && field.$invalid) {
          return 'has-error';
        } else {
          return '';
        }
      },
      createNewAccounting: function () {
        if (!this.formstate.$valid) {
          return;
        }
        var image_name = $.trim(this.model.name);
        resources.Accounting.create({image_name: image_name})
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
      },
      validatePath: function(value) {
        return (value.length === 0 || value[0] === '/');
      }
    },
    watch: {
      "model.volume_source": function(value) {
        var model = this.model;
        model.volume_source_target = [value, model.volume_target];
      },
      "model.volume_target": function(value) {
        var model = this.model;
        model.volume_source_target = [model.volume_source, value];
      },
      "model.volume_source_target": function(value) {
        var model = this.model;
        var formstate = this.formstate;
        var volume_source = value[0];
        var volume_target = value[1];
        if (formstate.volume_source.$invalid || formstate.volume_target.$invalid) {
          delete formstate.volume_source.$error.volumesInconsistent;
          delete formstate.volume_target.$error.volumesInconsistent;
          return;
        }
        if ((volume_source.length === 0 && volume_target.length !== 0) ||
            (volume_source.length !== 0 && volume_target.length === 0)) {
            formstate.volume_source.$invalid = true;
            formstate.volume_source.$valid = false;
            formstate.volume_source.$error.volumesInconsistent = true;
            formstate.volume_target.$invalid = true;
            formstate.volume_target.$valid = false;
            formstate.volume_target.$error.volumesInconsistent = true;
        } else {
          formstate.volume_source.$invalid = false;
          formstate.volume_source.$valid = true;
          delete formstate.volume_source.$error.volumesInconsistent;
          formstate.volume_target.$invalid = false;
          formstate.volume_target.$valid = true;
          delete formstate.volume_target.$error.volumesInconsistent;
        }
        
      },
      "show": function (value) {
        if (value) {
          this.reset();
        }
      }
    }
  };
});





/*
var ok_callback = function () {
  var image_name = $.trim($("#image_name").val());
  var allow_home = $("#allow_home").prop("checked");
  var volume_source = $.trim($("#volume_source").val());
  var volume_target = $.trim($("#volume_target").val());
  var volume_readonly = $("#volume_readonly").prop("checked");

  $(dialog).find(".alert").hide();

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
});
*/

