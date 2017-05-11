define([
    "utils",
    "components/vue/dist/vue"
], function(utils, Vue) {
    "use strict";

    var resolution_tag = 'resolution';
    var resolution_component = Vue.component(resolution_tag + '-component', {
        // Your configurable must have a "config_dict" property from the model
        props: ['config_dict'],

        template:
            '<div class="form-group">' +
            '  <label>Resolution</label>' +
            '  <select class="form-control" v-model="resolution">' +
            '    <option v-for="resolution_option in resolution_options">' +
            '      {{resolution_option}}' +
            '    </option>' +
            '  </select>' +
            '</div>',

        data: function() {
            return {
                resolution: this.config_dict.resolution,
                resolution_options: ['Window', '1920x1080', '1280x1024', '1280x800', '1024x768']
            };
        },

        watch: {
            config_dict: function() { this.resolution = this.config_dict.resolution; }, // model -> view update
            resolution: function() { this.$emit('update:config_dict', { resolution: this.resolution }); } // view -> model update
        }
    });

    // Your configurable class must implement a tag and default config_dict
    var ResolutionModel = function() {
        this.tag = resolution_tag;
        this.config_dict = { resolution: 'Window' };
    };

    ResolutionModel.prototype.as_config_dict = function() {
        var resolution = this.config_dict.resolution;

        if (resolution === 'Window') {
            var max_size = utils.max_iframe_size();
            resolution = max_size[0] + 'x' + max_size[1];
        }

        return { resolution: resolution };
    };

    // Export all your configurable models here
    return {
        resolution: ResolutionModel,
        resolution_component: resolution_component
    };
});
