define([
    '../../components/vue/dist/vue.min',
], function (Vue) {
    'use strict';

    var ApplicationListView = Vue.extend({
        template:
            '<section class="sidebar">' +
              '<!-- Search form -->' +
              '<form action="#" class="sidebar-form">' +
              '  <input type="text" name="q" class="form-control" placeholder="Search..." v-model="search_input">' +
              '</form>' +

              '<!-- Sidebar Menu -->' +
              '<ul class="sidebar-menu">' +
              '  <li class="header">APPLICATIONS</li>' +
              '</ul>' +

              '<ul id="applistentries" class="sidebar-menu">' +
              '  <li v-show="!model.loading && model.app_list.length === 0">' +
              '    <a href="#">No applications found</a>' +
              '  </li>' +

              '  <!-- Loading spinner -->' +
              '  <li v-show="model.loading" id="loading-spinner">' +
              '    <a href="#">' +
              '      <i class="fa fa-spinner fa-spin"></i>' +
              '      <span>Loading</span>' +
              '    </a>' +
              '  </li>' +

              '  <!-- Application list -->' +
              '  <li v-for="(app, index) in visible_list"' +
              '      :class="{ active: index === model.selected_index }"' +
              '      @click="model.selected_index = index; $(\'iframe\').focus();">' +

              '    <span :class="app.status.toLowerCase() + \'-badge\'"></span>' +

              '    <a href="#" class="truncate">' +
              '      <img class="app-icon"' +
              '           :src="app.app_data.image.icon_128 | icon_src">' +

              '      <button class="stop-button"' +
              '              v-if="app.is_running()"' +
              '              @click="model.stop_application(index)"' +
              '              :disabled="app.is_stopping()">' +
              '        <i class="fa fa-times"></i>' +
              '      </button>' +
              '      <span>{{ app.app_data.image | app_name }}</span>' +
              '    </a>' +
              '  </li>' +
              '</ul>' +
              '<!-- /.sidebar-menu -->' +
            '</section>' +
            '<!-- /.sidebar -->',

        data: function() {
            return { 'search_input': '' };
        },

        computed: {
            visible_list: function() {
                return this.model.app_list.filter(function(app) {
                    var app_name = this.$options.filters.app_name(app.app_data.image).toLowerCase();
                    return app_name.indexOf(this.search_input.toLowerCase()) !== -1;
                }.bind(this));
            }
        }
    });

    return {
        ApplicationListView : ApplicationListView
    };
});
