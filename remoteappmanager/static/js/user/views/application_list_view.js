let Vue = require("vuejs");
require("toolkit");

const ApplicationListView = Vue.extend({
    template:
          `<section class="sidebar">
            <!-- Error dialog -->
            <confirm-dialog v-if="stoppingError.show"
                            :title="'Error when stopping ' + stoppingError.appName"
                            :okCallback="closeDialog">
              <div class="alert alert-danger">
                <strong>Code: {{stoppingError.code}}</strong>
                <span>{{stoppingError.message}}</span>
              </div>
            </confirm-dialog>

          <!-- Search form -->
          <form action="#" class="sidebar-form">
            <input type="text" name="q" class="form-control" placeholder="Search..." v-model="searchInput">
          </form>

          <!-- Sidebar Menu -->
          <ul class="sidebar-menu">
            <li class="header">APPLICATIONS</li>
          </ul>

          <ul class="sidebar-menu">
            <li v-show="!model.loading && model.appList.length === 0" id="no-app-msg">
              <a href="#">No applications found</a>
            </li>

            <!-- Loading spinner -->
            <li v-show="model.loading" id="loading-spinner">
              <a href="#">
                <i class="fa fa-spinner fa-spin"></i>
                <span>Loading</span>
              </a>
            </li>
          </ul>

            <!-- Application list -->
          <transition-group name="list" tag="ul" id="applistentries" class="sidebar-menu">
            <li v-for="app in visibleList" v-bind:key="app"
                :class="{ active: indexOf(app) === model.selectedIndex }"
                @click="model.selectedIndex = indexOf(app); $emit('entryClicked');">

              <span :class="app.status.toLowerCase() + '-badge'"></span>

              <a href="#" class="truncate">
                <img class="app-icon"
                     :src="app.appData.image.icon_128 | iconSrc">

                <button class="stop-button"
                        v-if="app.isRunning()"
                        @click="stopApplication(indexOf(app))"
                        :disabled="app.isStopping()">
                  <i class="fa fa-times"></i>
                </button>
                <span>{{ app.appData.image | appName }}</span>
              </a>
            </li>
          </transition-group>
          <!-- /.sidebar-menu -->
        </section>
        <!-- /.sidebar -->`,

    data: function() {
        return {
            'searchInput': '',
            stoppingError: { show: false, appName: '', code: '', message: '' }
        };
    },

    computed: {
        visibleList: function() {
            return this.model.appList.filter((app) => {
                let appName = this.$options.filters.appName(app.appData.image).toLowerCase();
                return appName.indexOf(this.searchInput.toLowerCase()) !== -1;
            });
        }
    },

    methods: {
        stopApplication: function(index) {
            let stoppingAppName = this.$options.filters.appName(
                this.model.appList[index].appData.image);
            this.model.stopApplication(index).fail((error) => {
                this.stoppingError.code = error.code;
                this.stoppingError.message = error.message;
                this.stoppingError.appName = stoppingAppName;
                this.stoppingError.show = true;
            });
        },
        closeDialog: function() {
            this.stoppingError.show = false;
        },
        indexOf: function(app) {
            return this.model.appList.indexOf(app);
        }
    }
});

module.exports = {
    ApplicationListView
};
