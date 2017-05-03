define([
    "jquery",
    "handlebars",
    "utils",
    "components/vue/dist/vue.min"
], function($, hb, utils, Vue) {
    "use strict";

    var ResolutionModel = Vue.component('app-resolution', {
        template:
            '<div class="form-group">' +
            '  <label for="resolution-model-{{index}}">Resolution</label>' +
            '  <select class="form-control" v-model="resolution">' +
            '    <option v-for="resolution_option in resolution_options"'+
            '            value="resolution_option">resolution_option' +
            '    </option>' +
            '</div>',

        data: function() {
            return {
                resolution_options = ['Window', '1920x1080', '1280x1024', '1280x800', '1024x768']
            };
        }
    });

    /*ResolutionModel.prototype.tag = "resolution";

    ResolutionModel.prototype.as_config_dict = function() {
        // Returns the configuration dict to hand over to the API request.
        // e.g.
        // {
        //    "resolution" : "1024x768"
        // }
        // The returned dictionary must be added to the configurable
        // parameter under the key given by the tag member.
        var resolution = this.resolution;

        if (resolution === 'Window') {
            var max_size = utils.max_iframe_size();
            resolution = max_size[0] + 'x' + max_size[1];
        }

        return { 'resolution': resolution };
    };

    // Define all your configurables here.
    var configurables = {
        ResolutionModel: ResolutionModel
    };

    var from_tag = function (tag) {
        // Given a tag, lookup the appropriate configurable and
        // return it. If the tag matches no configurable, returns null
        for (var conf in configurables) {
            if (configurables[conf].prototype.tag === tag) {
                return configurables[conf];
            }
        }
        return null;
    };

    var ns = {
        from_tag: from_tag
    };

    return $.extend(ns, configurables);*/

});
