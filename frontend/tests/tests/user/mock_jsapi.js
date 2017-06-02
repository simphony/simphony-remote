var $ = require("jquery");

module.exports = {
  Application:  {
    data: {
      "12345": {
        image: {
          name: "app1",
          ui_name: "Application 1",
          icon_128: "",
          description: "This is obviously application 1",
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
        },
        container: {
          url_id: "654321"
        }
      },
      "51993": {
        image: {
          name: "app3",
          ui_name: "Application 3",
          icon_128: "",
          description: "This is application 3",
          policy: {
            allow_home: false,
            volume_source: "foo",
            volume_target: "bar",
            volume_mode: "baz"
          },
          configurables: []
        }
      },
    },
    create: function() {
    },
    delete: function() {
    },
    retrieve: function(id) {
      return $.when(this.data[id]);
    },
    items: function() {
      return $.when(["12345", "67890"], this.data);
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
