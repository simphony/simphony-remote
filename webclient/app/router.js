import Ember from 'ember';
import config from './config/environment';

const Router = Ember.Router.extend({
  location: config.locationType,
  rootUrl: config.rootUrl
});

Router.map(function() {
});

export default Router;
