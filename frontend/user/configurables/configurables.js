let utils = require("utils");

require("./Resolution");
require("./StartupData");


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

class StartupDataModel {
  constructor() {
    this.tag = "startupdata";
    this.configDict = { startupdata: '' };
  }

  asConfigDict() {
    let startupdata = this.configDict.startupdata;

    return { startupdata: startupdata };
  }
}

let outputConfigurables = {};

// Export all your configurable models here respecting the tag (here resolution)
outputConfigurables.resolution = ResolutionModel;
outputConfigurables.startupdata = StartupDataModel;

module.exports = outputConfigurables;
