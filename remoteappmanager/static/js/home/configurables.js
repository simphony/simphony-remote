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
            '  <select class="form-control" v-model="output">' +
            '    <option v-for="resolution_option in resolution_options">' +
            '      {{resolution_option}}' +
            '    </option>' +
            '  </select>' +
            '</div>',

        data: function() {
            return {
                output: this.value,
                resolution_options: ['Window', '1920x1080', '1280x1024', '1280x800', '1024x768']
            };
        },

        // Your configurable must implement a computed property config_dict
        computed: {
            config_dict: function() {
                var resolution = this.output;

                if (this.output === 'Window') {
                    var max_size = utils.max_iframe_size();
                    resolution = max_size[0] + 'x' + max_size[1];
                }

                return { 'resolution': resolution };
            }
        },

        watch: {
            value: function() {this.output = this.value},
            output: function() {this.$emit('update:output', this.output)},
            config_dict: function() {this.$emit('update:config_dict', this.config_dict)}
        }
    });

    // Export all your configurables here with the proper name
    return {
        resolution: { tag: resolution_tag, default: 'Window' }
    };
});
