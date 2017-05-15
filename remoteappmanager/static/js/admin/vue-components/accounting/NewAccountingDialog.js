var resources = require("resources");

module.exports = {
    template:
        '  <modal-dialog>' +
        '    <div class="modal-header"><h4>Create New Policy</h4></div>' +
        '    <div class="modal-body">' +
        '      <vue-form :state="formstate" v-model="formstate" @submit.prevent="createNewAccounting">' +
        '        <validate auto-label class="form-group required-field" :class="fieldClassName(formstate.image_name)">' +
        '          <label class="control-label">Image Name</label>' +
        '          <input type="text" name="image_name" class="form-control" required v-model="model.image_name">' +
        '          <field-messages name="image_name" show="$dirty || $submitted">' +
        '            <span class="help-block" slot="required">Image Name cannot be empty</span>' +
        '          </field-messages>' +
        '        </validate>' +
        '        ' +
        '        <div class="form-group">' +
        '            <label>' +
        '              <input type="checkbox" id="allow_home" v-model="model.allow_home"/> Mount home as Workspace' +
        '            </label>' +
        '        </div>' +
        '        ' +
        '        <validate auto-label class="form-group" :custom="{validatePath: validatePath}" :class="fieldClassName(formstate.volume_source)">' +
        '          <div class="form-group">' +
        '              <label for="volume_source">Volume Source</label>' +
        '              <input type="text" class="form-control" name="volume_source" placeholder="/local/path" v-model="model.volume_source"/>' +
        '          </div>' +
        '          <field-messages name="volume_source">' +
        '            <span class="help-block" slot="validatePath">Volume Source must be empty or an absolute path</span>' +
        '          </field-messages>' +
        '        </validate>' +
        '        ' +
        '        <validate auto-label :custom="{validatePath: validatePath}" class="form-group" :class="fieldClassName(formstate.volume_target)">' +
        '          <div class="form-group">' +
        '              <label for="volume_target">Volume Target</label>' +
        '              <input type="text" class="form-control" name="volume_target" placeholder="/container/path" v-model="model.volume_target"/>' +
        '          </div>' +
        '          <field-messages name="volume_target">' +
        '            <span class="help-block" slot="validatePath">Volume Target must be empty or an absolute path</span>' +
        '          </field-messages>' +
        '        </validate>' +
        '        ' +
        '        <div class="form-group">' +
        '          <label>' +
        '            <input type="checkbox" name="volume_readonly" v-model="model.volume_readonly" /> Mount volume readonly' +
        '          </label>' +
        '        </div>' +
        '           ' +
        '        <p v-if="crossValidationError" class="text-danger">Both Volume Source and Target must be defined</p>' +
        '        <div class="modal-footer">' +
        '          <div class="alert alert-danger" v-if="communicationError">' +
        '            <strong>Error:</strong> {{communicationError}}' +
        '          </div>' +
        '          <button type="button" class="btn btn-default" @click="close()">Cancel</button>' +
        '          <button class="btn btn-primary" type="submit" :disabled="formstate.$invalid">Submit</button>' +
        '        </div>' +
        '      </vue-form> ' +
        '    </div>' +
        '</modal-dialog>',

    props: ['show', "userId"],

    data: function () {
        return {
            formstate: {},
            crossValidationError: false,
            communicationError: null,
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
            var model = this.model;
            var formstate = this.formstate;

            if (formstate.$invalid) {
                return;
            }
            if ((model.volume_source.length === 0 && model.volume_target.length !== 0) ||
                (model.volume_source.length !== 0 && model.volume_target.length === 0)) {
                this.crossValidationError = true;
                return;
            }

            var rep = {
                user_id: this.userId,
                image_name: this.model.image_name,
                allow_home: this.model.allow_home,
                volume_source: this.model.volume_source,
                volume_target: this.model.volume_target,
                volume_mode: (model.volume_readonly ? "ro" : "rw")
            };

            resources.Accounting.create(rep)
            .done(function () {
                this.$emit('created');
            }.bind(this))
            .fail(function () {
                this.communicationError = "The request could not be executed successfully";
            }.bind(this));
        },

        reset: function () {
            Object.assign(this.$data, this.$options.data());
        },

        validatePath: function(value) {
            return (value.length === 0 || value[0] === '/');
        }
    },

    watch: {
        "show": function (value) {
            if (value) {
                this.reset();
            }
        },
        "model.volume_source": function() {
            delete this.formstate.volume_source.$error.volumesInconsistent;
            delete this.formstate.volume_target.$error.volumesInconsistent;
        },
        "model.volume_target": function() {
            delete this.formstate.volume_source.$error.volumesInconsistent;
            delete this.formstate.volume_target.$error.volumesInconsistent;
        }
    }
};
