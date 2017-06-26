// Load CSS (this CSS will be included in the bundle of CSS by webpack)
require('bootstrap-css');
require('font-awesome-css');
require('ionicons-css');
require('ionicons-css');
require('admin-lte-css');
require('skin-black-css');
require('skin-red-css');

// Load JS (Global jQuery so that it's accessible by bootstrap)
window.jQuery = window.$ = require('jquery');
require('admin-lte/plugins/slimScroll/jquery.slimscroll.min');
require('bootstrap');
require('admin-lte');
