odoo.define('cortex_documents.action_button_upload_attachment', function (require) {
    "use strict";

    var KanbanController = require('web.KanbanController');

    KanbanController.include({
        renderButtons: function($node) {
            this._super.apply(this, arguments);
            if (this.modelName === "cortex.document") {
                var data = this.model.get(this.handle);
                if (data.context.hide_button) {
                    this.$buttons.find('.o_button_upload_attachment').hide();
                }
                else {
                    this.$buttons.find('.o_button_upload_attachment').click(this.proxy('action_upload_attachment'));
                }
            }
        },
        /**
        * @private
        * @param {MouseEvent} event
        */
        action_upload_attachment: function () {
            var self = this;
            this._rpc({
                model: 'cortex.document',
                method: 'call_upload_wizard',
                args: [""],
            }).then(function (result) {
                return self.do_action(result);
            });
        },
    });
});