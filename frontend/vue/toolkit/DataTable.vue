<template>
  <div class="column-container">
    <div class="align-right">
      <button v-for="(action, action_index) in globalActions"
      :id="'global-action-' + action_index" class="btn btn-primary"
      @click="action.callback">{{action.label}}</button>
    </div>
    <div class="table-responsive">
      <table class="table table-hover no-margin">
        <thead>
          <tr>
            <th v-for="header in headers">{{header}}</th>
            <th v-if="rowActions.length > 0">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, row_index) in rows">
            <template v-for="(value, col_index) in row">
              <td v-if="isBoolean(value)"><i class="fa fa-check" v-if="value"></i></td>
              <td v-else>{{value}}</td>
            </template>
            <td>
              <button v-for="(action, action_index) in rowActions"
              :id="'row-' + row_index + '-action-' + action_index"
              :class="buttonClassFromType(action.type)"
              style="margin-right: 10px"
              @click="action.callback(row)">{{action.label}}</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
  module.exports = {
    props: [
      "headers", "rows", "globalActions", "rowActions"
    ],
    methods: {
      isBoolean: function(value) {
        return typeof(value) === "boolean";
      },
      buttonClassFromType: function(value = "danger") {
        let cls = {"btn": true};
        cls["btn-" + value] = true;
        return cls;
      }
    }
  };
</script>

<style scoped>
  .column-container {
    display: flex;
    flex-direction: column;
  }

  .align-right {
    align-self: flex-end;
  }
</style>
