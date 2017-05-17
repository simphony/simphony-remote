let resources = require("admin-resources");
let NewAccountingDialog = require("./accounting/NewAccountingDialog");

module.exports = {
  components: {
    'new-accounting-dialog': NewAccountingDialog
  },

  template:
    `<adminlte-box>
      <div slot="header">Accounting for user {{ $route.params.id }} </div>
      <div>
      <div class="alert alert-danger" v-if="communicationError">
        <strong>Error:</strong> {{communicationError}}
      </div>
      <data-table
       :headers.once="table.headers"
       :rows="table.rows"
       :globalActions="table.globalActions"
       :rowActions="table.rowActions">
      </data-table>
      <new-accounting-dialog
        v-if="newAccountingDialog.show"
        :show="newAccountingDialog.show"
        :userId="newAccountingDialog.userId"
        @created="newAccountingCreated"
        @closed="newAccountingDialog.show = false">
      </new-accounting-dialog>
      <confirm-dialog
         v-if="removeAccountingDialog.show"
         title="Remove Accounting"
         :okCallback="removeAccounting"
         :closeCallback="closeRemoveAccountingDialog">
        <div>Do you want to remove accounting
           {{ removeAccountingDialog.accountingToRemove }}?
        </div>
      </confirm-dialog>
      </div>
    </adminlte-box>`,

  data: function () {
    return {
      table: {
        headers: [
          "ID", "Image", "Workspace", "Vol. source", "Vol. target", "Readonly"
        ],
        rows: [],
        globalActions: [{
          label: "Create New Entry",
          callback: () => { this.newAccountingDialog.show = true; }
        }],
        rowActions: [{
          label: "Remove",
          callback: this.removeAction
        }]
      },

      newAccountingDialog: {
        show: false,
        userId: this.$route.params.id
      },

      removeAccountingDialog: {
        show: false,
        accountingToRemove: null
      },

      communicationError: null
    };
  },

  mounted: function () {
    this.updateTable();
  },

  methods: {
    updateTable: function() {
      this.communicationError = null;
      resources.Accounting.items({filter: JSON.stringify({user_id: this.$route.params.id })})
      .done((identifiers, items) => {
        this.table.rows = [];
        identifiers.forEach((id) => {
          let item = items[id];
          this.table.rows.push([
            id,
            item.image_name,
            item.allow_home,
            item.volume_source,
            item.volume_target,
            item.volume_mode === "ro"
          ]);
        });
      })
      .fail(() => {
        this.communicationError = "The request could not be executed successfully";
      });
    },

    newAccountingCreated: function() {
      this.newAccountingDialog.show = false;
      this.updateTable();
    },

    removeAction: function(row) {
      this.removeAccountingDialog.accountingToRemove = row[0];
      this.removeAccountingDialog.show = true;
    },

    closeRemoveAccountingDialog: function() {
      this.removeAccountingDialog.show = false;
      this.removeAccountingDialog.accountingToRemove = null;
    },

    removeAccounting: function () {
      resources.Accounting.delete(this.removeAccountingDialog.accountingToRemove)
      .done(() => {
        this.closeRemoveAccountingDialog();
        this.updateTable();
      })
      .fail(() => {
        this.closeRemoveAccountingDialog();
        this.communicationError = "The request could not be executed successfully";
      });
    }
  }
};

