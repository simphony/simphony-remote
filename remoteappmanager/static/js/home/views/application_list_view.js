define([
    '../../components/vue/dist/vue.min',
], function (Vue) {
    'use strict';

    var ApplicationListView = Vue.extend({
        template:
            '<section class="sidebar">' +

              '<!-- Search form -->' +
              '<form action="#" method="get" class="sidebar-form">' +
              '  <div class="input-group">' +
              '    <input type="text" name="q" class="form-control" placeholder="Search...">' +
              '    <span class="input-group-btn">' +
              '      <button type="submit" name="search" id="search-btn" class="btn btn-flat"><i class="fa fa-search"></i>' +
              '      </button>' +
              '    </span>' +
              '  </div>' +
              '</form>' +

              '<!-- Sidebar Menu -->' +
              '<ul id="applistentries" class="sidebar-menu">' +
              '  <li class="header">APPLICATIONS</li>' +

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
              '  <li v-for="(app, index) in model.app_list"' +
              '      :class="{ active: index === model.selected_index }"' +
              '      @click="model.selected_index = index; $emit(\'focus_iframe\');">' +

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
            '<!-- /.sidebar -->'
    });

    return {
        ApplicationListView : ApplicationListView
    };
});
