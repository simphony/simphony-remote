<template>
  <section class="sidebar">
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
  </section>
</template>

<script>
  let Vue = require("vuejs");
  require("toolkit");

  module.exports = Vue.extend({
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
</script>

<style scoped>
  #applistentries > li > a > div {
    float: left;
  }

  #applistentries img.app-icon {
    position: relative;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    border-color: black;
    border-width: 1px;
    border-style: solid;
    margin-right: 5px;
    margin-top: -2px;
    background-color: white;
  }

  .running-badge {
    display: block;
    position: absolute;
    top: 24px;
    left: 8px;
    z-index: 100;
    width: 4px;
    height: 4px;
    border: 1px solid darkcyan;
    background-color: cyan;
    border-radius: 50%;
    box-shadow: 0px 0px 8px rgba(0, 255, 255, 1.0)
  }

  .stopped-badge {
    display: block;
    position: absolute;
    top: 24px;
    left: 8px;
    z-index: 100;
    width: 4px;
    height: 4px;
    border: 1px solid transparent;
    background-color: transparent;
    border-radius: 50%;
    box-shadow: 0px 0px 8px rgba(0, 0, 0, 1.0);
  }

  .starting-badge {
    display: block;
    position: absolute;
    top: 24px;
    left: 8px;
    z-index: 100;
    width: 4px;
    height: 4px;
    border: 1px solid yellow;
    background-color: lightyellow;
    border-radius: 50%;
    box-shadow: 0px 0px 8px rgba(255, 255, 0, 1.0);
    animation: starting-pulse 2s infinite;
  }

  .stopping-badge {
    display: block;
    position: absolute;
    top: 24px;
    left: 8px;
    z-index: 100;
    width: 4px;
    height: 4px;
    border: 1px solid darkred;
    background-color: red;
    border-radius: 50%;
    box-shadow: 0px 0px 8px rgba(255, 0, 0, 1.0);
    animation: stopping-pulse 2s infinite;
  }

  @keyframes starting-pulse {
    0% {
      background-color: lightyellow;
      box-shadow: 0px 0px 8px rgba(255, 255, 0, 1.0);
      border: 1px solid yellow;
    }
    50% {
      background-color: #7F7F00;
      box-shadow: 0px 0px 8px rgba(127, 127, 0, 1.0);
      border: 1px solid #7F7F00;
    }
    0% {
      background-color: lightyellow;
      box-shadow: 0px 0px 8px rgba(255, 255, 0, 1.0);
      border: 1px solid yellow;
    }
  }

  @keyframes stopping-pulse {
    0% {
      background-color: red;
      box-shadow: 0px 0px 8px rgba(255, 0, 0, 1.0);
      border: 1px solid darkred;
    }
    50% {
      background-color: #7F0000;
      box-shadow: 0px 0px 8px rgba(127, 0, 0, 1.0);
      border: 1px solid #7F0000;
    }
    0% {
      background-color: red;
      box-shadow: 0px 0px 8px rgba(255, 0, 0, 1.0);
      border: 1px solid darkred;
    }
  }

  .truncate {
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .stop-button {
    display: none;
    position: absolute;
    top: 10px;
    left: 15px;
    z-index: 100;
    width: 32px;
    height: 32px;
    padding: 0px;
    border: 1px solid rgba(0, 0, 0, 0.8);
    background-color: rgba(0, 0, 0, 0.7);
    border-radius: 50%;
    font-size: 18px;
    color: rgba(255, 255, 255, 0.7);
  }

  /* When the mouse is on the img or the stop-button -> display stop-button */
  li a img:hover + .stop-button {
    display: block;
  }
  li a .stop-button:hover {
    display: block;
  }
</style>

<style>
  .list-enter, .list-leave-to {
    opacity: 0;
    transform: translateX(-50px);
  }
  .list-enter-active, .list-leave-active {
    transition: all 0.5s;
    position: absolute;
  }
  .list-move {
    transition: transform .5s;
  }
</style>
