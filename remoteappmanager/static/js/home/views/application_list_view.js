define([
    'utils',
    '../../components/vue/dist/vue.min',
], function (utils, Vue) {
    'use strict';

    /* Create application_list ViewModel
    (will next be wrapped in a main ViewModel which will contain the
    applicationListView and the applicationView) */
    var ApplicationListView = Vue.extend({
        filters: utils.filters
    });

    return {
        ApplicationListView : ApplicationListView
    };
});
