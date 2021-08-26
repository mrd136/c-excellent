odoo.define('custom_pos_receipt.product_domain',function(require) {
    "use strict";
    var models = require("point_of_sale.models");
    var Screens = require("point_of_sale.screens");
    var core = require('web.core');
    var _t  = require('web.core')._t;
    var rpc = require('web.rpc');
    var ProductProduct = _.find(models.PosModel.prototype.models, function(p){
        return p.model == 'product.product';
    });
    var ResPartner = _.find(models.PosModel.prototype.models, function(p){
        return p.model == 'res.partner';
    });

    models.load_models([
        {
            model:  'pos.neighborhood',
            fields: ['name', 'pos_config_id','country','state','delivery_fees'],
            loaded: function(self,neighborhoods){
                ProductProduct.domain = [['id', 'not in', self.config.exepted_products],['available_in_pos','=',true]];
                self.neighborhoods = neighborhoods;
            },
        }],{'before': 'product.product'});

    models.load_fields('res.partner','neighborhood_id');
    models.load_fields('res.partner','delivery_fees');
    //models.load_fields('res.partner','is_pos_partner');
    models.load_fields('product.pricelist','pricelist_type');
    //ResPartner.domain = [['is_pos_partner','=', true]];
    var ProductProduct = _.find(models.PosModel.prototype.models, function(p){
        return p.model == 'product.product';
    });
    ProductProduct.fields.push('ar_trans');
    ProductProduct.fields.push('en_trans');
    models.Orderline = models.Orderline.extend({
        export_for_printing: function(){
            return {
                quantity:           this.get_quantity(),
                unit_name:          this.get_unit().name,
                price:              this.get_unit_display_price(),
                discount:           this.get_discount(),
                product_name:       this.get_product().display_name,
                product_name_wrapped: this.generate_wrapped_product_name(),
                price_lst:          this.get_lst_price(),
                display_discount_policy:    this.display_discount_policy(),
                price_display_one:  this.get_display_price_one(),
                price_display :     this.get_display_price(),
                price_with_tax :    this.get_price_with_tax(),
                price_without_tax:  this.get_price_without_tax(),
                price_with_tax_before_discount:  this.get_price_with_tax_before_discount(),
                tax:                this.get_tax(),
                product_description:      this.get_product().description,
                product_description_sale: this.get_product().description_sale,
                //extra_items: this.get_extra_items(),
                product_ar_trans : this.get_product().ar_trans,
                product_en_trans : this.get_product().en_trans,
            };
        },
    });
    models.Order = models.Order.extend({
        get_product_name : function(product_id) {
            var name = this.pos.db.get_product_by_id(product_id).name;
            return name;
        },
        get_product_default_code : function(product_id) {
            var default_code = this.pos.db.get_product_by_id(product_id).default_code;
            return default_code;
        },
        computeChanges: function(categories){
            var current_res = this.build_line_resume();
            var old_res     = this.saved_resume || {};
            var json        = this.export_as_JSON();
            var add = [];
            var rem = [];
            var line_hash;

            for ( line_hash in current_res) {
                var curr = current_res[line_hash];
                var old  = old_res[line_hash];

                if (typeof old === 'undefined') {
                    add.push({
                        'id':       curr.product_id,
                        'name':     this.pos.db.get_product_by_id(curr.product_id).display_name,
                        'name_wrapped': curr.product_name_wrapped,
                        'note':     curr.note,
                        'qty':      curr.qty,
                        'name_base': this.pos.db.get_product_by_id(curr.product_id).name,
                        'default_code': this.pos.db.get_product_by_id(curr.product_id).default_code,

                    });
                } else if (old.qty < curr.qty) {
                    add.push({
                        'id':       curr.product_id,
                        'name':     this.pos.db.get_product_by_id(curr.product_id).display_name,
                        'name_wrapped': curr.product_name_wrapped,
                        'note':     curr.note,
                        'qty':      curr.qty - old.qty,
                        'name_base': this.pos.db.get_product_by_id(curr.product_id).name,
                        'default_code': this.pos.db.get_product_by_id(curr.product_id).default_code,
                    });
                } else if (old.qty > curr.qty) {
                    rem.push({
                        'id':       curr.product_id,
                        'name':     this.pos.db.get_product_by_id(curr.product_id).display_name,
                        'name_wrapped': curr.product_name_wrapped,
                        'note':     curr.note,
                        'qty':      old.qty - curr.qty,
                        'name_base': this.pos.db.get_product_by_id(curr.product_id).name,
                        'default_code': this.pos.db.get_product_by_id(curr.product_id).default_code,
                    });
                }
            }

            for (line_hash in old_res) {
                if (typeof current_res[line_hash] === 'undefined') {
                    var old = old_res[line_hash];
                    rem.push({
                        'id':       old.product_id,
                        'name':     this.pos.db.get_product_by_id(old.product_id).display_name,
                        'name_wrapped': old.product_name_wrapped,
                        'note':     old.note,
                        'qty':      old.qty,
                        'name_base': this.pos.db.get_product_by_id(curr.product_id).name,
                        'default_code': this.pos.db.get_product_by_id(curr.product_id).default_code,
                    });
                }
            }

            if(categories && categories.length > 0){
                // filter the added and removed orders to only contains
                // products that belong to one of the categories supplied as a parameter

                var self = this;

                var _add = [];
                var _rem = [];

                for(var i = 0; i < add.length; i++){
                    if(self.pos.db.is_product_in_category(categories,add[i].id)){
                        _add.push(add[i]);
                    }
                }
                add = _add;

                for(var i = 0; i < rem.length; i++){
                    if(self.pos.db.is_product_in_category(categories,rem[i].id)){
                        _rem.push(rem[i]);
                    }
                }
                rem = _rem;
            }

            var d = new Date();
            var hours   = '' + d.getHours();
                hours   = hours.length < 2 ? ('0' + hours) : hours;
            var minutes = '' + d.getMinutes();
                minutes = minutes.length < 2 ? ('0' + minutes) : minutes;

            return {
                'new': add,
                'cancelled': rem,
                'table': json.table || false,
                'floor': json.floor || false,
                'name': json.name  || 'unknown order',
                'time': {
                    'hours':   hours,
                    'minutes': minutes,
                },
            };

        },
    });

    Screens.ActionpadWidget.include({
        renderElement: function() {
            var self = this;
            this._super();
            this.$('.pay').click(function(){
                var order = self.pos.get_order();
                var flag = false;

                if(order.orderlines.models.length == 0){
                    flag = true;
                    alert("Select at least one product !");
                    self.gui.show_screen('products');
                    return;
                }
                if(order.delivery_type=='delivery'){
                    var client = order.get_client();
                    if(!client){
                        flag = true;
                        alert("Please select a customer !");
                        self.gui.show_screen('products');
                        return;
                    }
                }
                for (var i = 0; i < order.orderlines.models.length; i++) {
                    if(order.orderlines.models[i].get_base_price() <=0){
                        if('promotion' in order.orderlines.models[i].attributes){
                            continue;
                        }
                        if(order.pricelist.pricelist_type === 'employee'){
                            continue;
                        }
                        if(typeof order.return_ref === 'undefined'){
                            flag = true;
                            alert("price must be greater than zero !");
                            self.gui.show_screen('products');
                            return;
                        }
                    }
                }
                if(order.delivery_type=='delivery'){
                    for (var i = 0; i < order.orderlines.models.length; i++) {
                        if(order.orderlines.models[i].product.type=='service'){
                            order.remove_orderline(order.orderlines.models[i]);
                        }
                    }

                    var fields = ProductProduct.fields;
                    rpc.query({
                        model: 'product.product',
                        method: 'search_read',
                        args: [[['name', 'ilike', 'Delivery'],['type', '=', 'service']], fields],
                        limit: 1,
                    })
                    .then(function (ord){
                        if (ord){
                            var product = self.pos.db.get_product_by_id(ord[0].id);
                            var new_line = new models.Orderline({}, {pos: self.pos, order: order, product: product});
                            new_line.set_quantity(1);
                            if(order.get_client().delivery_fees){
                                new_line.set_unit_price(order.get_client().delivery_fees);
                            }
                            else{
                                new_line.set_unit_price(0);
                            }
                            order.add_orderline(new_line);
                        }
                    });

                }
                if (!flag){
                    return;
                }
                var has_valid_product_lot = _.every(order.orderlines.models, function(line){
                    return line.has_valid_product_lot();
                });
                if(!has_valid_product_lot){
                    self.gui.show_popup('confirm',{
                        'title': _t('Empty Serial/Lot Number'),
                        'body':  _t('One or more product(s) required serial/lot number.'),
                        confirm: function(){
                            if (!flag){
                                self.gui.show_screen('payment');
                            }
                        },
                    });
                }else{
                    if (!flag){
                        self.gui.show_screen('payment');
                    }
                }
            });
            this.$('.set-customer').click(function(){
                self.gui.show_screen('clientlist');
            });
        }
    });

    Screens.PaymentScreenWidget.include({
        renderElement: function() {
            var self = this;
            this._super();
            this.$('.next').click(function(){
                var order = self.pos.get_order();
                if (order.is_paid()) {
                    var buttons = self.pos.gui.screen_instances.products.action_buttons;
                    if (buttons.submit_order){
                        buttons.submit_order.button_click();
		            }
                    return;
                }
                return;
            });

        }
    });

});
