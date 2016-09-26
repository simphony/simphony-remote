define(function (require) {
    "use strict";
    var MockApi = function () {
        this.available_applications_info = function () {
            return [{
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
                },
                mapping_id: "12345"
            },
                {
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
                    },
                    mapping_id: "67890"
                }];
        };
    };

    return {
        MockApi:  MockApi
    };
});
