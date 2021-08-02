odoo.define('pos_order_orderline_remark.pos_order_orderline_remark',function(require){
    "use strict"

    var core = require('web.core');
    var gui = require('point_of_sale.gui');
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var session = require('web.session')
    var _t = core._t;
    var _super_orderline = models.Orderline.prototype;
    var is_pos_restaurant_install = _.contains(session.module_list, 'pos_restaurant');

    models.Orderline = models.Orderline.extend({
        initialize: function(attr, options) {
            _super_orderline.initialize.call(this,attr,options);
            this.note = this.note || "";
            this.is_pos_restaurant_install =  is_pos_restaurant_install;
        },
        set_note: function(note){
            this.note = note;
            this.trigger('change',this);
        },
        get_note: function(note){
            return this.note;
        },
        generate_wrapped_product_name: function() {
            var MAX_LENGTH = 24; // 40 * line ratio of .6
            var wrapped =   _super_orderline.generate_wrapped_product_name.apply(this,arguments);
           
            //For product comment wrapped
            if(this.note && this.get_note()){
                if(this.get_note().length > 0){
                    var order_line_comment = (this.get_note().length > 0) ? " - "+this.get_note() : this.get_note();
                    var current_order_line_comment = "";

                    while (order_line_comment.length > 0) {
                        var comment_space_index = 23;//name.indexOf(" ");

                        if (comment_space_index === -1) {
                            comment_space_index = order_line_comment.length;
                        }

                        if (current_order_line_comment.length + comment_space_index > MAX_LENGTH) {
                            if (current_order_line_comment.length) {
                                wrapped.push(current_order_line_comment);
                            }
                            current_order_line_comment = "";
                        }

                        current_order_line_comment += order_line_comment.slice(0, comment_space_index + 1);
                        order_line_comment = order_line_comment.slice(comment_space_index + 1);
                    }

                    if (current_order_line_comment.length) {
                        wrapped.push(current_order_line_comment);
                    }
                }
            }

            return wrapped;
        },
        can_be_merged_with: function(orderline) {
            if (orderline.get_note() !== this.get_note()) {
                return false;
            } else {
                return _super_orderline.can_be_merged_with.apply(this,arguments);
            }
        },
        clone: function(){
            var orderline = _super_orderline.clone.call(this);
            orderline.note = this.note;
            return orderline;
        },
        export_as_JSON: function(){
            var json = _super_orderline.export_as_JSON.call(this);
            json.note = this.note;
            return json;
        },
        init_from_JSON: function(json){
            _super_orderline.init_from_JSON.apply(this,arguments);
            this.note = json.note;
        },
        export_for_printing: function() {
            var json = _super_orderline.export_for_printing.apply(this,arguments);
            json.note = this.get_note();
            return json;  
        },
    });
    // if(!is_pos_restaurant_install){
    var OrderlineNoteButton = screens.ActionButtonWidget.extend({
        template: 'OrderlineNoteButton',
        button_click: function(){
            var self = this;
            var line = this.pos.get_order().get_selected_orderline();
            if (line) {
                this.gui.show_popup('textarea',{
                    title: _t('Add Line Note'),
                    value:   line.get_note(),
                    confirm: function(note) {
                        line.set_note(note);
                    },
                });
            }
        },
    });
    screens.define_action_button({
        'name': 'orderline_note',
        'widget': OrderlineNoteButton,
        'condition': function(){
            return this.pos.config.orderline_note && !this.pos.config.module_pos_restaurant;
        },
    });
    // }

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function(attr,options) {
            _super_order.initialize.apply(this,arguments);
        },
        set_remark: function(note){
            this.order_remark = note;
            this.trigger('change',this);
        },
        get_remark: function(){
            if(this.order_remark){
                return this.order_remark
            }
            return '';
        },
        init_from_JSON: function(json){
            _super_order.init_from_JSON.apply(this,arguments);
            this.order_remark = json.order_remark;
        },
        export_for_printing: function() {
            var json = _super_order.export_for_printing.apply(this,arguments);
            json.order_remark = this.get_remark();
            return json;  
        },
        export_as_JSON : function(json) {
            var json = _super_order.export_as_JSON.apply(this,arguments);
            json.order_remark = this.get_remark();
            return json;
        },
    })

    var OrderRemarkButton = screens.ActionButtonWidget.extend({
        template: 'OrderRemarkButton',
        button_click: function(){
            var order = this.pos.get_order();
            var line = order.get_selected_orderline();
            if (line) {
                this.gui.show_popup('textarea',{
                    title: _t('Add Order Note'),
                    value: order.get_remark(),
                    confirm: function(note) {
                        order.set_remark(note);
                    },
                });
            }
        },
    });

    screens.define_action_button({
        'name': 'order_remark',
        'widget': OrderRemarkButton,
        'condition': function(){
            return this.pos.config.order_remark;
        },
    });

})
