odoo.define('techno_pos_session_report.session_report', function (require) {
"use strict";

var gui = require('point_of_sale.gui');
var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');
var core = require('web.core');
var ActionManager = require('web.ActionManager');

var QWeb = core.qweb;

var SessionReportPrintButton = screens.ActionButtonWidget.extend({
    template: 'SessionReportPrintButton',
    button_click: function(){
        var self = this;
        var pos_session_id = self.pos.pos_session.id;
        var action = {
            'type': 'ir.actions.report',
            'report_type': 'qweb-pdf',
            'report_file': 'techno_pos_session_report.report_pos_session_pdf/'+pos_session_id.toString(),
            'report_name': 'techno_pos_session_report.report_pos_session_pdf/'+pos_session_id.toString(),
            'data': self.data,
            'context': {'active_id': [pos_session_id]},
        };
        return this.do_action(action);
    },
});

screens.define_action_button({
    'name': 'session_report_print',
    'widget': SessionReportPrintButton,
    'condition': function(){ 
        return this.pos.config.iface_session_report;
    },
});
return {
    SessionReportPrintButton: SessionReportPrintButton,
};
});
