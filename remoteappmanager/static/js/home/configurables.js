define([
    "utils",
    "components/vue/dist/vue.min"
], function(utils, Vue) {
    "use strict";

    var resolution_conf_tag = 'resolution';
    var resolution_component = Vue.component(resolution_conf_tag + '-component', {
        // Your configurable must have a "value" property
        props: ['value'],

        template:
            '<div class="form-group">' +
            '  <label>Resolution</label>' +
            '  <select class="form-control" v-model="selected_value">' +
            '    <option v-for="resolution_option in resolution_options">' +
            '      {{resolution_option}}' +
            '    </option>' +
            '  </select>' +
            '</div>',

        data: function() {
            return {
                selected_value: this.value,
                resolution_options: ['Window', '1920x1080', '1280x1024', '1280x800', '1024x768']
            };
        },

        watch: {
            value: function() {this.selected_value = this.value;}, // model -> view update
            selected_value: function() {this.$emit('update:value', this.selected_value);} // view -> model update
        }
    });

    // Your configurable class must implement tag and value attributes and as_config_dict method
    var ResolutionModel = function() {
        this.tag = resolution_conf_tag;
        this.value = 'Window';
        this.component = resolution_component;
    };
    ResolutionModel.prototype.as_config_dict = function() {
        var resolution = this.value;

        if (this.value === 'Window') {
            var max_size = utils.max_iframe_size();
            resolution = max_size[0] + 'x' + max_size[1];
        }

        return { 'resolution': resolution };
    };

    // Export all your configurable models here
    return {
        resolution: ResolutionModel
    };
});
