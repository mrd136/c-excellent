odoo.define('aspl_pos_combo.pos', function (require) {
"use strict";

	var models = require('point_of_sale.models');
	var gui = require('point_of_sale.gui');
	var screens = require('point_of_sale.screens');
	var PopupWidget = require('point_of_sale.popups');
	var PosBaseWidget = require('point_of_sale.BaseWidget');

    var core = require('web.core');
    var rpc = require('web.rpc');
    var utils = require('web.utils');
    var field_utils = require('web.field_utils');
    var BarcodeEvents = require('barcodes.BarcodeEvents').BarcodeEvents;

    var QWeb = core.qweb;
    var _t = core._t;

    var round_pr = utils.round_precision;

    // LET'S START CODING

	models.load_fields("product.product", ['is_combo','product_combo_ids', 'pos_price_tot', 'price_supplement', 'can_sale_pos_solo','when_be_sale']);
	models.load_fields("pos.order.line", ['is_splmnt','real_supplement_price']);

    models.PosModel.prototype.models.push({
        model:  'kzm.pos.supplement',
        fields: ['product_id', 'price_supplement', 'based_on_priceliste'],
        loaded: function(self,product_combo_line){
            self.product_combo_line = product_combo_line;
        },

    });


	models.PosModel.prototype.models.push({
        model:  'product.combo',
        loaded: function(self,product_combo){
            self.product_combo = product_combo;
        },
    });

    screens.ProductListWidget.include({


        renderElement: function() {
        //this._super(parent,options)
        var el_str  = QWeb.render(this.template, {widget: this});
        var el_node = document.createElement('div');
            el_node.innerHTML = el_str;
            el_node = el_node.childNodes[1];

        if(this.el && this.el.parentNode){
            this.el.parentNode.replaceChild(el_node,this.el);
        }
        this.el = el_node;

        var list_container = el_node.querySelector('.product-list');
        for(var i = 0, len = this.product_list.length; i < len; i++){
            //this.set_unit_price(this.product.get_price(this.order.pricelist, this.get_quantity()))
            var product_node = this.render_product(this.product_list[i]);
            product_node.addEventListener('click', this.click_product_handler);
            product_node.addEventListener('keypress', this.keypress_product_handler);
            //console.log("=== PRODUCT:", this.product_list[i].display_name, ", AFFICHER SUR LES MENU SEUL:",this.product_list[i].can_sale_pos_solo);
            if(!this.product_list[i].can_sale_pos_solo){
                if(this.product_list[i].when_be_sale && this.product_list[i].when_be_sale.length > 0){
                    if(this.product_list[i].when_be_sale.indexOf(this.pos.config.id) >= 0){
                        list_container.appendChild(product_node);
                    }
                }else{
                    list_container.appendChild(product_node);
                }

            }
        }
    },

    });

//    var _super_product = models.Product.prototype;
//    models.Product = models.Product.extend({
//    get_price: function(pricelist, quantity){
//        var self = this;
//        var price = _super_product.get_price.call(this, pricelist, quantity);
//        return price ;// AMH_ADD supplement price
//    },
//
//    });

	var _super_Order = models.Order.prototype;
	models.Order = models.Order.extend({
		add_product: function(product, options){
        	var self = this;
        	_super_Order.add_product.call(this, product, options);
        	if(product.is_combo && product.product_combo_ids.length > 0 && self.pos.config.enable_combo){
        		self.pos.gui.show_popup('combo_product_popup',{
        			'product':product
        		});
        	}
		},
        // get_subtotal : function(){
        //     var res =  _super_Order.get_subtotal.call(this,arguments);
        //     console.log("--- get_subtotal:", res);
        //     return res;
        // },
        get_total_with_tax: function() {
            var res =  _super_Order.get_total_with_tax.call(this,arguments);
            res = round_pr(res, 0.1);
            return res;
        },
        // get_total_without_tax: function() {
        //     var res =  _super_Order.get_total_without_tax.call(this,arguments);
        //     console.log("--- get_total_without_tax:", res);
        //     return res;
        // },
        // get_total_discount: function() {
        //     var res =  _super_Order.get_total_discount.call(this,arguments);
        //     console.log("--- get_total_discount:", res);
        //     return res;
        // },
	});

	var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
    	initialize: function(attr,options){
            this.combo_prod_info = false;
            this.is_splmnt = (options.is_splmnt)?options.is_splmnt:false;
            this.real_supplement_price = (options.real_supplement_price)?options.real_supplement_price:false;
            _super_orderline.initialize.apply(this, arguments);
            console.log("Order line initialize: pos combo aspl module");
        },
        set_combo_prod_info: function(combo_prod_info){
        	this.combo_prod_info = combo_prod_info;
        	var supp_price = this.price
        	for(var i=0; i< this.combo_prod_info.length; i++){
        	    supp_price += this.combo_prod_info[i].product_detail.price_supplement;
        	}
        	this.set_unit_price(supp_price);
        },
        get_combo_prod_info: function(){
//        console.log("++++ GET +++");
//        console.log(this.combo_prod_info);
//        console.log("++++ END GET +++");
        	return this.combo_prod_info;
        },
        export_as_JSON: function(){
            var self = this;
            var json = _super_orderline.export_as_JSON.call(this,arguments);
            var combo_ext_line_info = [];
            if(this.product.is_combo && this.combo_prod_info.length > 0){
                _.each(this.combo_prod_info, function(item){
                    //console.log("---- JSON:", item.real_supplement_price, item.price, item.display_name);//correct
                	combo_ext_line_info.push([0, 0, {'product_id':item.product.id, 'qty':item.qty, 'price':item.price,
                	'is_splmnt':true,
                	'real_supplement_price': item.real_supplement_price}]);
                });
            }
            json.combo_ext_line_info = this.product.is_combo ? combo_ext_line_info : [];
            //console.log("=============================================");
            //console.info(json);
           // console.log("=============================================");
            return json;
        },
        can_be_merged_with: function(orderline){
        	var result = _super_orderline.can_be_merged_with.call(this,orderline);
        	if(orderline.product.id == this.product.id && this.get_combo_prod_info()){
        		return false;
        	}
        	return result;
        },
        export_for_printing: function(){
            var lines = _super_orderline.export_for_printing.call(this);
            var new_attr = {
            	combo_prod_info: this.get_combo_prod_info(),
            }
            $.extend(lines, new_attr);
            return lines;
        },

    });

	var POSComboProductPopup = PopupWidget.extend({
        template: 'POSComboProductPopup',
        events: _.extend({}, PopupWidget.prototype.events, {
    		'click .collaps_div': 'collaps_div',
    		'click .product.selective_product': 'select_product',
    		'click .confirm_amh': 'click_confirm_amh',
    	}),
        show: function(options){
        	var self = this;
            this._super(options);
            this.product = options.product || false;
            var combo_products_details = [];
            this.new_combo_products_details = [];
            this.product.product_combo_ids.map(function(id){
            	var record = _.find(self.pos.product_combo, function(data){
            		return data.id === id;
            	});
            	combo_products_details.push(record);
            });

            combo_products_details.map(function(combo_line){
        		var details = [];
        		var new_product_ids = [];
        		if(combo_line.product_ids.length > 0){
        			combo_line.product_ids.map(function(combo_line_id){
        			// AMH_ADDED
        			var combo_line_obj = _.find(self.pos.product_combo_line, function(data){
                                        return data.id === combo_line_id;
                                    });

                    var product_id = combo_line_obj.product_id[0];
        			var obj_product_id = self.pos.db.get_product_by_id(product_id);
                    if(!obj_product_id){
                        alert("L'article <"+combo_line_obj.product_id[0]+" : "+combo_line_obj.product_id[1]+ ">\n n'existe pas, archivé ou n'est pas disponible sur le PDV");
                        return;
                    }
                    var is_supplement = !(combo_line_obj.based_on_priceliste);

                    var pricelist_price = combo_line_obj.price_supplement;
                    if(!is_supplement){
                        pricelist_price = obj_product_id.get_price(self.pos.get_order().pricelist, 1);
                    }
                    
        			//alert(product_id);
        			//console.log("Product "+product_id + " ::",obj_product_id);
//        			console.log("++++");
//        			console.log(obj_product_id);
//        			console.log("-------");
        			// END AMH_ADDED
                    
        			    new_product_ids.push(product_id);
        				if(combo_line.require){
        					var data = {
        					    'is_supplement': true,//show all compansant in ticket//is_supplement && pricelist_price > 0,
                        		'no_of_items': combo_line.no_of_items,
                        		'product_id': product_id,
                        		'category_id': combo_line.pos_category_id[0] || false,
                        		'used_time': combo_line.no_of_items,
                        		'price_supplement': pricelist_price,//,// AMH_ADDED
                        		'price_supplement_str': self.format_currency(pricelist_price,'Supp Price'),// AMH_ADDED
                        		'sale_price': obj_product_id.pos_price_tot,// AMH_ADDED
                        		'sale_price_str': self.format_currency(obj_product_id.pos_price_tot,'Product Price'),
                        	}
            				details.push(data);
        				}else{
        				    //console.log("==++= PRODUCT ID:",product_id);
        				    //console.log("== COMBO LINE:", combo_line);
        					var data = {
        					    'is_supplement': true,//show all compansant in ticket//is_supplement && pricelist_price > 0,
                        		'no_of_items': combo_line.no_of_items,
                        		'product_id': product_id,
                        		'category_id': combo_line.pos_category_id[0] || false,
                        		'used_time': 0,
                        		'price_supplement': pricelist_price,//combo_line_obj.price_supplement,// AMH_ADDED
                        		'price_supplement_str': self.format_currency(pricelist_price,'Supp Price'),// AMH_ADDED
                        		'sale_price': obj_product_id.pos_price_tot,// AMH_ADDED
                        		'sale_price_str': self.format_currency(obj_product_id.pos_price_tot,'Product Price'),
                        	}
            				details.push(data);
        				}
        			});
        			self.new_combo_products_details.push({
        				'id':combo_line.id,
        				'no_of_items':combo_line.no_of_items,
        				'pos_category_id':combo_line.pos_category_id,
        				'product_details':details,
        				'product_ids':new_product_ids,
        				'combo_lines': combo_line.product_ids,
        				'require':combo_line.require,
        			});
        		}
            });


            this.renderElement();
        },
        collaps_div: function(event){
        	if($(event.currentTarget).hasClass('fix_products')){
        		$('.combo_header_body').slideToggle('500');
        		$(event.currentTarget).find('i').toggleClass('fa-angle-down fa-angle-up');
        	}else if($(event.currentTarget).hasClass('selective_products')){
        		$('.combo_header2_body').slideToggle('500');
        		$(event.currentTarget).find('i').toggleClass('fa-angle-down fa-angle-up');
        	}
        },
        select_product: function(event){
        	var self = this;
        	var $el = $(event.currentTarget);
        	var product_id = Number($el.data('product-id'));
        	var category_id = Number($el.data('categ-id'));
        	if($(event.target).hasClass('fa-times') || $(event.target).hasClass('product-remove')){
        		if($el.hasClass('selected')){
        			self.new_combo_products_details.map(function(combo_line){
                		if(!combo_line.require){
                			if(combo_line.pos_category_id[0] == category_id && (_.contains(combo_line.product_ids, product_id))){
                				combo_line.product_details.map(function(product_detail){
                					if(product_detail.product_id == product_id){
                						product_detail.used_time = 0;
                					}
                				});
                			}
                		}
                	});
            	}
        	}else{
            	self.new_combo_products_details.map(function(combo_line){
            		if(!combo_line.require){//if not require
            		//console.log(combo_line.pos_category_id);
            		//console.log(combo_line.product_ids);
            		if((_.contains(combo_line.product_ids, product_id))){
            			//if(combo_line.pos_category_id[0] == category_id && (_.contains(combo_line.product_ids, product_id))){
            				var added_item = 0;
            				combo_line.product_details.map(function(product_detail){
            					added_item += product_detail.used_time;
            				});
            				combo_line.product_details.map(function(product_detail){
            					if(product_detail.product_id == product_id){
            						if(product_detail.no_of_items > product_detail.used_time && product_detail.no_of_items > added_item){
            							product_detail.used_time += 1;
            						}
            					}
            				});
            			}
            		}
            	});
        	}


        	self.renderElement();
        },
        click_confirm_amh: function(){
            var self = this;
            var order = self.pos.get_order();
//            var total_amount = 0;
            var products_info = [];
            var pricelist = self.pos.gui.screen_instances.products.product_list_widget._get_active_pricelist();

            //Begin AMH ADDED: used times Verification
            var nb_used =  0, nb_no_of_items = 0, nb_used_level = 0, nb_level_no = 0;
                self.new_combo_products_details.map(function(combo_line){
                    nb_no_of_items += combo_line.no_of_items;
                    nb_used_level = 0;
                    if(!combo_line.require){//if not require
                            combo_line.product_details.map(function(product_detail){
                                    nb_used_level += product_detail.used_time;

                             });
                    }else{
                        nb_used_level = combo_line.no_of_items;
                    }
                    nb_used += nb_used_level;
                    if(nb_used_level != combo_line.no_of_items){
                            nb_level_no += 1;
                    }
            	});
            //End AMH ADDES: Verification used times done
            if(nb_level_no > 0){
                alert("Vérifier vos choix de tous les niveaux du menu !\n "+ nb_level_no +" niveaux incomplets\n "+nb_used+"/"+nb_no_of_items +" Articles choisis");
            	return false;
            }else{
            self.new_combo_products_details.map(function(combo_line){
            	if(combo_line.product_details.length > 0){
            		combo_line.product_details.map(function(prod_detail){
            			if(prod_detail.used_time){
            				var product = self.pos.db.get_product_by_id(prod_detail.product_id);
                            //console.log("-----",product.display_name, prod_detail.price_supplement);//correct
                			if(product){
//                				total_amount = self.product.get_price(pricelist, 1);
                				products_info.push({
                				"product":product,
                				'qty':prod_detail.used_time,
                				//BE 'price':product.get_price(pricelist, 1),
                				'real_supplement_price':prod_detail.price_supplement,
                				'price':0,
                				'product_detail': prod_detail,
                				});
                			}

            			}
            		});
            	}
            });
            var selected_line = order.get_selected_orderline();
            if(products_info.length > 0){
            	if(selected_line){
//            		selected_line.set_unit_price(total_amount);
            		selected_line.set_combo_prod_info(products_info);
            		self.pos.chrome.screens.products.order_widget.rerender_orderline(selected_line);
            	}else{
            		alert("Selected line not found!");
            	}
            }else{
            	if(selected_line){
            		order.remove_orderline(selected_line);
            	}
            }
            self.gui.close_popup();
            }
        },
        click_cancel: function(){
        	var order = this.pos.get_order();
        	var selected_line = order.get_selected_orderline();
        	if(selected_line){
        		order.remove_orderline(selected_line);
        	}
        	this.gui.close_popup();
        },
    });
    gui.define_popup({name:'combo_product_popup', widget: POSComboProductPopup});

});