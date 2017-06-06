// Load CSS (this CSS will be included in the bundle of CSS by webpack)
require('bootstrap-css');

// Load JS (Global jQuery so that it's accessible by bootstrap)
window.jQuery = window.$ = require('jquery');
require('bootstrap');
require('admin-lte');
