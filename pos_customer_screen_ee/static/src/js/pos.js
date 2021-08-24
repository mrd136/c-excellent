odoo.define('pos_customer_screen_ee.pos', function (require) {
"use strict";

    var bus_service = require('bus.BusService');
    var bus = require('bus.Longpolling');
	var pos_model = require('point_of_sale.models');
	var rpc   = require('web.rpc');
	var session = require('web.session');
	var screens = require('point_of_sale.screens');
	var chrome = require('point_of_sale.chrome');
	var PosBaseWidget = require('point_of_sale.BaseWidget');
	var core = require('web.core');
	var models = require('point_of_sale.models');

	var _t = core._t;

	chrome.Chrome.include({
          build_widgets:function(){
                var self = this;
                this._super();
                self.call('bus_service', 'updateOption','customer.display',session.uid);
                self.call('bus_service', 'onNotification', self, self._onNotification);
                self.call('bus_service', 'startPolling');
          },
          _onNotification: function(notifications){
                var self = this;
                 for (var notif of notifications) {
                    var order = self.pos.get_order();
                    if(notif[1].rating){
                        if(order){
                            order.set_rating(notif[1].rating);
                        }
                    }else if(notif[1].partner_id){
                        var partner_id = notif[1].partner_id;
                        var partner = self.pos.db.get_partner_by_id(partner_id);
                        if(partner){
                            if(order){
                                order.set_client(partner);
                            }
                        }else{
                            if(partner_id){
                                var fields = _.find(self.pos.models,function(model){ return model.model === 'res.partner'; }).fields;
                                var params = {
                                    model: 'res.partner',
                                    method: 'search_read',
                                    fields: fields,
                                    domain: [['id','=',partner_id]],
                                }
                                rpc.query(params, {async: false})
                                .then(function(partner){
                                    if(partner && partner.length > 0 && self.pos.db.add_partners(partner)){
                                        order.set_client(partner[0]);
                                    }else{
                                        alert("partner not loaded in pos.");
                                    }
                                });
                            }else{
                                console.info("Partner id not found!")
                            }
                        }
                    }
                 }
           },
     });

    screens.PaymentScreenWidget.include({
    	render_paymentlines: function(){
    		this._super();
    		var customer_display = this.pos.config.customer_display;
    		if(customer_display){
    			this.pos.get_order().mirror_image_data();
    		}
    	}
    });

    screens.ReceiptScreenWidget.include({
        renderElement: function() {
            var self = this;
            this._super();
            var customer_display = this.pos.config.customer_display;
            this.$('.next').click(function(){
            	if(self.pos.get_order()){
            		if(customer_display){
            			self.pos.get_order().mirror_image_data(true);
            		}
            	}
            });
        },
    });

    chrome.OrderSelectorWidget.include({
    	start: function(){
            this._super();
            var customer_display = this.pos.config.customer_display;
            if(this.pos.get_order()){
            	if(customer_display){
            		this.pos.get_order().mirror_image_data();
            	}
            }
    	},
    	renderElement: function(){
            var self = this;
            this._super();
            var customer_display = this.pos.config.customer_display;
            this.$('.order-button.select-order').click(function(event){
            	if(self.pos.get_order() && customer_display){
            		self.pos.get_order().mirror_image_data(true);
            	}
            });
            this.$('.neworder-button').click(function(event){
            	if(self.pos.get_order() && customer_display){
            		self.pos.get_order().mirror_image_data(true);
            	}
            });
            this.$('.deleteorder-button').click(function(event){
            	if(self.pos.get_order() && customer_display){
            		self.pos.get_order().mirror_image_data();
            	}
            });
        },
        deleteorder_click_handler: function(event, $el) {
            var self  = this;
            var order = this.pos.get_order();
            var customer_display = this.pos.config.customer_display;
            if (!order) {
                return;
            } else if ( !order.is_empty() ){
                this.gui.show_popup('confirm',{
                    'title': _t('Destroy Current Order ?'),
                    'body': _t('You will lose any data associated with the current order'),
                    confirm: function(){
                        self.pos.delete_current_order();
                        if(customer_display){
                        	self.pos.get_order().mirror_image_data(true);
                        }
                    },
                });
            } else {
                this.pos.delete_current_order();
                if(customer_display){
                	self.pos.get_order().mirror_image_data(true);
                }
            }
        },
    });

	var _modelproto = pos_model.Order.prototype;
	pos_model.Order = pos_model.Order.extend({
        add_product:function(product, options){
            var self = this;
            _modelproto.add_product.call(this,product, options);
            var customer_display = this.pos.config.customer_display;
            if(customer_display){
            	self.mirror_image_data();
            }
        },
        mirror_image_data:function(neworder){
            var self = this;
            var client_name = false;
            var order_total = self.get_total_with_tax();
            var change_amount = self.get_change();
            var payment_info = [];
            var paymentlines = self.paymentlines.models;
            if(paymentlines && paymentlines[0]){
            	paymentlines.map(function(paymentline){
            		payment_info.push({
            			'name':paymentline.name,
            			'amount':paymentline.amount,
            		});
            	});
            }
            if(self.get_client()){
            	client_name = self.get_client().name;
            }
            var vals = {
            	'cart_data':$('.order-container').html(),
            	'client_name':client_name,
            	'order_total':order_total,
            	'change_amount':change_amount,
            	'payment_info':payment_info,
            	'enable_customer_rating':self.pos.config.enable_customer_rating,
            	'set_customer':self.pos.config.set_customer,
            }
            if(neworder){
                vals['new_order'] = true;
            }
            rpc.query({
                model: 'customer.display',
                method: 'broadcast_data',
                args: [vals],
            })
            .then(function(result) {});
        },
        set_client: function(client){
        	_modelproto.set_client.apply(this, arguments);
    		this.mirror_image_data();
        },
        set_rating: function(rating){
            this.rating = rating;
        },
        get_rating: function(){
            return this.rating;
        },
        export_as_JSON: function() {
            var order = _modelproto.export_as_JSON.call(this);
            var new_val = {
            	rating: this.get_rating() || '0',
            }
            $.extend(order, new_val);
            return order;
    	},
    });

    screens.NumpadWidget.include({
        start: function() {
            var self = this;
            this._super();
            var customer_display = this.pos.config.customer_display;
            this.$(".input-button").click(function(){
            	if(customer_display){
            		self.pos.get_order().mirror_image_data();
            	}
            });
        },
    });

    var CustomerDisplay = screens.ActionButtonWidget.extend({
		template : 'CustomerDisplay',
		button_click : function() {
			self = this;
			window.open(self.pos.attributes.origin+'/web/customer_display' , '_blank');
		},
	});
	screens.define_action_button({
		'name' : 'CustomerDisplay',
		'widget' : CustomerDisplay,
		condition: function(){
			return this.pos.config.customer_display;
		},
	});
});