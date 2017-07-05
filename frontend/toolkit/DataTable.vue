<template>
  <div class="column-container">
    <div class="align-right">
      <button v-for="action in globalActions" class="btn btn-primary" @click="action.callback">{{action.label}}</button>
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
              <td v-html="format(value, col_index)"></td>
            </template>
            <td>
              <button v-for="action in rowActions"
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
  let _ = require('lodash');

  module.exports = {
    props: {
      headers: { type: Array, default: () => {return [];} },
      columnFormatters: { type: Array, default: () => {return [];} },
      rows: { type: Array, default: () => {return [];} },
      globalActions: { type: Array, default: () => {return [];} },
      rowActions: { type: Array, default: () => {return [];} }
    },
    methods: {
      buttonClassFromType: function(value = "danger") {
        let cls = {"btn": true};
        cls["btn-" + value] = true;
        return cls;
      },
      format: function(value, col_index) {
        if(_.isFunction(this.columnFormatters[col_index])) {
          return this.columnFormatters[col_index](value);
        }
        return value;
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
