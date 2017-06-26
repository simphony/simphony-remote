<template>
  <section class="sidebar">
    <!-- Search form -->
    <form action="#" class="sidebar-form">
      <input id="search-input" type="text" name="q" class="form-control" placeholder="Search..." v-model="searchInput">
    </form>

    <!-- Sidebar Menu -->
    <ul class="sidebar-menu">
      <li class="header">APPLICATIONS</li>

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
      :id="'application-entry-' + indexOf(app)"
      @click="model.selectedIndex = indexOf(app); $emit('entryClicked');">

        <span :class="app.status.toLowerCase() + '-badge'"></span>

        <a href="#" class="truncate">
          <img class="app-icon"
          :src="app.appData.image.icon_128 | iconSrc">

          <span>{{ app.appData.image | appName }}</span>
        </a>
      </li>
    </transition-group>
  </section>
</template>

<script>
  let Vue = require("vue");

  module.exports = Vue.extend({
    data: function() {
      return {
        'searchInput': ''
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
      indexOf: function(app) {
        return this.model.appList.indexOf(app);
      }
    }
  });
</script>

<style scoped>
  .app-icon {
    position: relative;
    width: 32px;
    height: 32px;
    border-radius: 20%;
    border-color: black;
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
    border-radius: 20%;
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

  .list-enter, .list-leave-to {
    opacity: 0;
    transform: translateX(-50px);
  }
  .list-enter-active, .list-leave-active {
    transition: all .5s;
  }
  .list-move {
    transition: transform .5s;
  }
</style>
