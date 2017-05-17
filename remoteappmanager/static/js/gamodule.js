// This module contains the setup for google analytics.
// MUST not be renamed to analytics. Some blockers rely on name
// matching to prevent loading.

function init() {
    if (window.apidata.analytics !== undefined) {
        window.ga('create', window.apidata.analytics.tracking_id, 'auto');
    } else {
        window.ga = function() {};
    }

    return function() {
        window.ga.apply(this, arguments);
    };
}

class GaObserver {
    constructor() {
        this.ga = init();
    }

    triggerApplicationStarting(name) {
        this.ga("send", "event", {
            eventCategory: "Application",
            eventAction: "start",
            eventLabel: name
        });
    }
}

module.exports = {
    init, // For testing purpose
    GaObserver
};
