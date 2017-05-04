define([
    "utils",
    "components/vue/dist/vue.min"
], function(utils, Vue) {
    "use strict";

    var resolution_tag = 'resolution-tag';
    Vue.component(resolution_tag, {
        template:
            '<div class="form-group">' +
            '  <label>Resolution</label>' +
            '  <select class="form-control" v-model="value">' +
            '    <option v-for="resolution_option in resolution_options">' +
            '      {{resolution_option}}' +
            '    </option>' +
            '</div>',

        // Your configurable must have a "value" data
        data: function() {
            return {
                value: 'Window',
                resolution_options: ['Window', '1920x1080', '1280x1024', '1280x800', '1024x768']
            };
        },

        // Your configurable must implement a computed property config_dict
        computed: {
            config_dict: function() {
                var resolution = this.resolution;

                if (this.resolution === 'Window') {
                    var max_size = utils.max_iframe_size();
                    resolution = max_size[0] + 'x' + max_size[1];
                }

                return { 'resolution': resolution };
            }
        }
    });

    // Export all your configurables here with the proper name
    return {
        resolution: { tag: resolution_tag, default: 'Window' }
    };
});
