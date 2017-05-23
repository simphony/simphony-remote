var ErrorDialog = require("./ErrorDialog");

var errorReceiver = [];

// Mount error dialog component
new ErrorDialog({
  el: '#error-dialog-container',
  data: function() { return {
    errorList: errorReceiver
  }; }
});

module.exports = errorReceiver;
