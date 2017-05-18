<template>
  <transition name="modal-fade">
    <div class="modal modal-display">
      <div class="modal-dialog">
        <div class="modal-content">
          <slot></slot>
        </div>
      </div>
    </div>
  </transition>
</template>

<style scoped>
  .modal-fade-enter-active, .modal-fade-leave-active {
    transition: opacity .2s
  }
  .modal-fade-enter, .modal-fade-leave-to {
    opacity: 0
  }

  .modal-display {
    display: block;
  }
</style>
