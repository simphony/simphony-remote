define([
    "utils",
    "components/vue/dist/vue"
], function(utils, Vue) {
    "use strict";

    var resolutionTag = 'resolution';
    var resolutionComponent = Vue.component(resolutionTag + '-component', {
        // Your configurable must have a "configDict" property from the model
        props: ['configDict'],

        template:
            '<div class="form-group">' +
            '  <label>Resolution</label>' +
            '  <select class="form-control" v-model="resolution">' +
            '    <option v-for="resolutionOption in resolutionOptions">' +
            '      {{resolutionOption}}' +
            '    </option>' +
            '  </select>' +
            '</div>',

        data: function() {
            return {
                resolution: this.configDict.resolution,
                resolutionOptions: ['Window', '1920x1080', '1280x1024', '1280x800', '1024x768']
            };
        },

        watch: {
            configDict: function() { this.resolution = this.configDict.resolution; }, // model -> view update
            resolution: function() { this.$emit('update:configDict', { resolution: this.resolution }); } // view -> model update
        }
    });

    // Your configurable class must implement a tag and default configDict
    var ResolutionModel = function() {
        this.tag = resolutionTag;
        this.configDict = { resolution: 'Window' };
    };

    ResolutionModel.prototype.asConfigDict = function() {
        var resolution = this.configDict.resolution;

        if (resolution === 'Window') {
            var maxSize = utils.maxIframeSize();
            resolution = maxSize[0] + 'x' + maxSize[1];
        }

        return { resolution: resolution };
    };

    var outputConfigurables = {};

    // Export all your configurable models here
    outputConfigurables[resolutionTag] = {
        model: ResolutionModel,
        component: resolutionComponent
    };

    return outputConfigurables;
});
