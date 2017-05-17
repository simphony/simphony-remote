var resources = require("admin-resources");

module.exports = {
    template:
        `    <modal-dialog>
              <div class="modal-header"><h4>Create New Application</h4></div>
              <div class="modal-body">
                <vue-form :state="formstate" v-model="formstate" @submit.prevent="createNewApplication">
                  <validate auto-label class="form-group required-field" :class="fieldClassName(formstate.name)">
                    <label class="control-label">Image Name</label>
                    <input type="text" name="name" class="form-control" required v-model.trim="model.name">
                      <field-messages name="name" show="$touched || $submitted">
                      <span class="help-block" slot="required">Image Name cannot be empty</span>
                    </field-messages>
                  </validate>
                  <div class="modal-footer">
                  <div class="alert alert-danger" v-if="communicationError">
                    <strong>Error:</strong> {{communicationError}}
                  </div>
                    <button type="button" class="btn btn-default" @click="close()">Cancel</button>
                    <button class="btn btn-primary" type="submit" :disabled="formstate.$invalid">Submit</button>
                  </div>
                </vue-form>
              </div>
          </modal-dialog>`,

    props: ['show'],

    data: function () {
        return {
            formstate: {},
            communicationError: null,
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

        createNewApplication: function () {
            if (!this.formstate.$valid) {
                return;
            }
            resources.Application.create({image_name: this.model.name})
            .done(() => {
                this.$emit('created');
            })
            .fail(() => {
                this.communicationError = "The request could not be executed successfully";
            });
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
