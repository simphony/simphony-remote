<template>
  <div class="row">
    <div class="col-md-12">
      <div class="box">
        <div class="box-header with-border">
          <h3 class="box-title">{{title}}</h3>
        </div>
        <div class="box-body"><slot></slot></div>
      </div>
    </div>
  </div>
</template>

<script>
  module.exports = {
    props: {
      title: {
        type: String,
        default: "Box"
      }
    }
  };
</script>
