odoo.define('pos_custom.models', function (require) {
"use strict";

    var field_utils = require('web.field_utils');
    var models = require('point_of_sale.models');
    var utils = require('web.utils');
    var round_pr = utils.round_precision;

    models.Orderline = models.Orderline.extend({
        set_quantity: function(quantity, keep_price){
            this.order.assert_editable();
            if(quantity === 'remove'){
                this.order.remove_orderline(this);
                return;
            }else{
                var quant = parseFloat(quantity) || 0;
                var unit = this.get_unit();
                if(unit){
                    if (unit.rounding) {
                        var decimals = this.pos.dp['Product Unit of Measure'];
                        var rounding = Math.max(unit.rounding, Math.pow(10, -decimals));
                        this.quantity    = round_pr(quant, rounding);
                        this.quantityStr = field_utils.format.float(this.quantity, {digits: [69, decimals]});
                    } else {
                        this.quantity    = round_pr(quant, 1);
                        this.quantityStr = this.quantity.toFixed(0);
                    }
                }else{
                    this.quantity    = quant;
                    this.quantityStr = '' + this.quantity;
                }
            }

            // just like in sale.order changing the quantity will recompute the unit price
    //        if(! keep_price && ! this.price_manually_set){
    //            this.set_unit_price(this.product.get_price(this.order.pricelist, this.get_quantity()));
    //            this.order.fix_tax_included_price(this);
    //        }
            this.trigger('change', this);
        }
    });
});