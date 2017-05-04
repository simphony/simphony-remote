define([
    "utils",
    "components/vue/dist/vue.min"
], function(utils, Vue) {
    "use strict";

    var resolution_tag = 'resolution';
    Vue.component(resolution_tag, {
        // Your configurable must have a "value" property
        props: ['value'],

        template:
            '<div class="form-group">' +
            '  <label>Resolution</label>' +
            '  <select class="form-control" v-model="sel_value">' +
            '    <option v-for="resolution_option in resolution_options">' +
            '      {{resolution_option}}' +
            '    </option>' +
            '  </select>' +
            '</div>',

        data: function() {
            return {
                sel_value: this.value,
                resolution_options: ['Window', '1920x1080', '1280x1024', '1280x800', '1024x768']
            };
        },

        watch: {
            value: function() {this.sel_value = this.value;}, // model -> view update
            sel_value: function() {this.$emit('update:value', this.sel_value);} // view -> model update
        }
    });

    // Export all your configurable models here
    // (must implement tag and value attributes and as_config_dict method)
    return {
        resolution: {
            tag: resolution_tag,
            value: 'Window',
            as_config_dict: function() {
                var resolution = this.value;

                if (this.value === 'Window') {
                    var max_size = utils.max_iframe_size();
                    resolution = max_size[0] + 'x' + max_size[1];
                }

                return { 'resolution': resolution };
            }
        }
    };
});
