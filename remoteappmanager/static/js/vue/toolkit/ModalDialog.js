module.exports = {
    template: `<transition name="modal-fade">
          <div class="modal modal-display">
            <div class="modal-dialog">
              <div class="modal-content">
                <slot>
                </slot>
              </div>
            </div>
          </div>
        </transition>`
};