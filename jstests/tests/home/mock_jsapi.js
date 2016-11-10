define(['jquery'], function ($) {
    "use strict";

    return {
        Application:  {
            create: function() {
            },
            delete: function() {
            },
            retrieve: function(id) {
                var data = {
                    "12345": {
                        image: {
                            name: "app1",
                            ui_name: "Application 1",
                            icon_128: "",
                            description: "description",
                            policy: {
                                allow_home: true,
                                volume_source: "",
                                volume_target: "",
                                volume_mode: ""
                            },
                            configurables: [
                                "resolution"
                            ]
                        }
                    },
                    "67890": {
                        image: {
                            name: "app2",
                            ui_name: "Application 2",
                            icon_128: "",
                            description: "description",
                            policy: {
                                allow_home: true,
                                volume_source: "",
                                volume_target: "",
                                volume_mode: ""
                            },
                            configurables: []
                        }
                    }
                };
                
                return $.when(data[id]);
                
            },
            items: function() {
                return $.when(["12345", "67890"]);
            }
        },
        Container:  {
            create: function() {
            },
            delete: function() {
            },
            retrieve: function() {
            },
            items: function() {
            }
        }
    };
});
