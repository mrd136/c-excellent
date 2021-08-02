odoo.define('pos_multi_note.notes_pos', function (require) {
    "use strict";
    var screens = require('point_of_sale.screens');
    var gui = require('point_of_sale.gui');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var PopupWidget = require('point_of_sale.popups');
    var _t = core._t;
    var models = require('point_of_sale.models');

    models.load_models({
        model: 'pos.order.note',
        fields: ['pos_note','menu_categ'],
        loaded: function (self, ordernotes) {
            self.order_note_by_id = {};
            for (var i = 0; i < ordernotes.length; i++) {
                self.order_note_by_id[ordernotes[i].id] = ordernotes[i];
            }
        }
    });

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function(attr,options) {
            this.delivery_type = 'takeaway';
            $('.delivery .fa').text(" Takeaway ");
            $('.delivery .fa').attr("class", "fa fa-shopping-bag");
            _super_order.initialize.apply(this,arguments);
        },
        set_note: function(note){
            this.old_note = this.note;
            this.note = this.old_note +'\n'+ note;
            this.trigger('change',this);
            this.trigger('new_updates_to_send');
            this.pos.gui.screen_instances.products.order_widget.renderElement(true);
        },
        get_delivery_type: function(){
            return this.delivery_type;
        },
        set_delivery_type: function(type){
            this.delivery_type = type;
            this.trigger('change',this);
            this.trigger('new_updates_to_send');
            this.pos.gui.screen_instances.products.order_widget.renderElement(true);
        },
        set_driver: function(id){
            this.delivery_guy_id = id;
            this.trigger('change',this);
            this.trigger('new_updates_to_send');
            this.pos.gui.screen_instances.products.order_widget.renderElement(true);
        },
        export_as_JSON: function() {
            var data = _super_order.export_as_JSON.apply(this, arguments);
            data.delivery_guy_id = this.delivery_guy_id;
            data.delivery_type = this.delivery_type;
            return data;
        },
        init_from_JSON: function(json) {
            this.delivery_guy_id = json.delivery_guy_id;
            this.delivery_type = json.delivery_type;
            _super_order.init_from_JSON.call(this, json);
        },
        clone: function(){
            var order = _super_order.clone.call(this);
            order.delivery_guy_id = this.delivery_guy_id;
            order.delivery_type = this.delivery_type;
            return order;
        },
    });

    var NotePopupWidget = PopupWidget.extend({
        count: 0,
        template: 'NotePopupWidget',
        events: _.extend({}, PopupWidget.prototype.events, {
            'change .note_temp': 'click_option',
            'click .button': 'click_option'
        }),
        init: function (parent, options) {
            this.options = options || {};
            this._super(parent, _.extend({}, {
                size: "medium"
            }, this.options));
        },
        renderElement: function () {
            this._super();
            for (var note in this.pos.order_note_by_id) {
                if(this.pos.get_order()){
                    if (this.pos.get_order().get_selected_orderline()){
                        if (this.pos.order_note_by_id[note].menu_categ[0] == this.pos.get_order().get_selected_orderline().product['pos_categ_id'][0]){
    //                        $('#note_select').append($("<option>" + this.pos.order_note_by_id[note].pos_note + "</option>").attr("value", this.pos.order_note_by_id[note].pos_note)
    //                            .attr("id", this.pos.order_note_by_id[note].id)
    //                            .attr("class", "note_option"))
                            $('#test').append($("<li><div class='button' style='width:auto;height:55px;' id='"+ this.pos.order_note_by_id[note].id +"'>" + this.pos.order_note_by_id[note].pos_note + "</div></li>"))
                        }
                    }
                }
            }
        },
        show: function (options) {
            options = options || {};
            this._super(options);
            $('textarea').text(options.value);
        },
        click_confirm: function (event) {
            event.preventDefault();
            event.stopPropagation();
            var line = this.pos.get_order().get_selected_orderline();
            //line.set_note($('#note_text_area').val());
	    line.old_note = line.note;
            line.note = line.old_note +'\n'+ $('#note_text_area').val();
            line.trigger('change',line);
            line.trigger('new_updates_to_send');
            this.pos.gui.screen_instances.products.order_widget.renderElement(true);
            this.gui.close_popup();
        },
        click_option: function (event) {
            event.preventDefault();
            event.stopPropagation();
            var old_text = $('textarea').val();
            var text = event.currentTarget.textContent;
            old_text += "\n";
            old_text += " - ";
            old_text += text;
            $('textarea').text(old_text);
        }

    });
    gui.define_popup({name: 'pos_no', widget: NotePopupWidget});

    var DeliveryPopupWidget = PopupWidget.extend({
        template: 'DeliveryPopupWidget',
        events: _.extend({}, PopupWidget.prototype.events, {
            'click .button': 'click_option'
        }),
        init: function (parent, options) {
            this.options = options || {};
            this._super(parent, _.extend({}, {
                size: "medium"
            }, this.options));
        },
        click_confirm: function (event) {
            event.preventDefault();
            event.stopPropagation();
            var self = this;
            var order = this.pos.get_order();
            if($('#delivery').hasClass('active')){
                var select = document.getElementById("del_select");
                if (select.value=='') {
                    self.gui.show_popup('error', {
                        'title': _t('Select a driver'),
                        'body': _t('Please select delivery guy for this order , if there is no delivery guy in the list please add them from POS configuration'),
                    });
                    return;
                }
                var options = select.options;
                var id = options[options.selectedIndex].id;
                var value = options[options.selectedIndex].value;
                order.delivery_type = 'delivery';
                order.set_delivery_type(order.delivery_type);
                order.delivery_guy_id = id;
                order.set_driver(id);
                $('.delivery .fa').text(" Delivery ");
                $('.delivery .fa').attr("class", "fa fa-motorcycle");
            }
            if($('#internal').hasClass('active')){
                order.delivery_type = 'internal';
                order.set_delivery_type(order.delivery_type);
                $('.delivery .fa').text(" Internal ");
                $('.delivery .fa').attr("class", "fa fa-home");
            }
            if($('#takeaway').hasClass('active')){
                order.delivery_type = 'takeaway';
                order.set_delivery_type(order.delivery_type);
                $('.delivery .fa').text(" Takeaway ");
                $('.delivery .fa').attr("class", "fa fa-shopping-bag");
            }
            this.gui.close_popup();
        },
        click_option: function (event) {
            event.preventDefault();
            event.stopPropagation();
            $('#takeaway').attr('class','button');
            $('#internal').attr('class','button');
            $('#delivery').attr('class','button');
            event.currentTarget.className += " active";
            var text = event.currentTarget.textContent;
            var id = event.currentTarget.id;
            if(id=='delivery'){
                var drivers = this.pos.config.delivery_guy_ids;
                $('#del_select').find('option').remove().end()
                for (var i = 0; i < drivers.length; i++) {
                    rpc.query({
                        model: "hr.employee",
                        method: "search_read",
                        args: [[["id", "=", drivers[i]]]],
                        limit: 1,
                    })
                    .then(function (employee){
                        $('#del_select').append($("<option id='"+ employee[0].id +"'>" + employee[0].name + "</option>"))
                    });
                }
                $('#del_li').attr('style','');
            }
            if(id!='delivery'){
                $('#del_li').attr('style','display:none;');
            }
        }

    });
    gui.define_popup({name: 'delivery', widget: DeliveryPopupWidget});
    var DeliveryButton = screens.ActionButtonWidget.extend({
        template: 'DeliveryButton',
        button_click: function () {
            this.gui.show_popup('delivery');
        }
    });

    screens.define_action_button({
        'name': 'pos_delivery',
        'widget': DeliveryButton,
    });

    var InternalNoteButton = screens.ActionButtonWidget.extend({
        template: 'InternalNoteButton',
        button_click: function () {
            var line = this.pos.get_order().get_selected_orderline();
            if (line) {
                this.gui.show_popup('pos_no', {
                    value: line.get_note(),
                    'title': _t('ADD YOUR MULTIPLE ORDER NOTES')
                });
            }
        }
    });

    screens.define_action_button({
        'name': 'pos_internal_note',
        'widget': InternalNoteButton,
        'condition': function () {
            return this.pos.config.note_config;
        }
    });
    return {
    DeliveryButton: DeliveryButton,
    InternalNoteButton: InternalNoteButton
    }
});

