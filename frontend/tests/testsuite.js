window.apidata = {
  base_url: "/user/lambda",
  prefix: "/"
};

require("./tests/user/test_configurables.js");
require("./tests/user/test_models.js");
require("./tests/user/test_application_list_view.js");
require("./tests/user/test_application_view.js");
require("./tests/user/test_application_label.js");
require("./tests/vue/components/test_DataTable.js");
require("./tests/vue/components/test_ConfirmDialog.js");
require("./tests/vue/components/test_error_dialog.js");
require("./tests/test_utils.js");
require("./tests/test_analytics.js");
