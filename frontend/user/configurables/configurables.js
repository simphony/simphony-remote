let utils = require("utils");

require("./Resolution");


// Your configurable class must implement a tag and default configDict
class ResolutionModel {
  constructor() {
    this.tag = 'resolution';
    this.configDict = { resolution: 'Window' };
  }

  asConfigDict() {
    let resolution = this.configDict.resolution;

    if (resolution === 'Window') {
      let maxSize = utils.maxIframeSize();
      resolution = maxSize[0] + 'x' + maxSize[1];
    }

    return { resolution: resolution };
  }
}

let outputConfigurables = {};

// Export all your configurable models here respecting the tag (here resolution)
outputConfigurables.resolution = ResolutionModel;

module.exports = outputConfigurables;
