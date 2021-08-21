odoo.define("tis_pos_receipt.models", function (require) {
"use strict";

    var utils = require('web.utils');
    var round_pr = utils.round_precision;
    var models = require('point_of_sale.models');
    var core = require('web.core');
    var qweb = core.qweb;
    var _t = core._t;

    models.load_fields('res.company', ['street','street2','city','state_id','vat', 'name_arabic', 'street_arabic', 'street2_arabic', 'city_arabic', 'state_arabic']);
    models.load_fields('product.product',['name','name_arabic']);

    var _super_Orderline = models.Orderline.prototype;
        models.Orderline = models.Orderline.extend({
            initialize: function (attributes, options) {
                var res = _super_Orderline.initialize.apply(this, arguments);
                return res;
            },
            init_from_JSON: function (json) {
                var res = _super_Orderline.init_from_JSON.apply(this, arguments);

            },



            export_for_printing: function () {
                console.log('export_for_printing')
                var receipt_line = _super_Orderline.export_for_printing.apply(this, arguments);
                console.log('receipt_line',receipt_line)
                receipt_line['product_name_arabic'] = this.generate_arabic_product_name();
                console.log('receipt_line_arabic',receipt_line)
                return receipt_line;

            },

            generate_arabic_product_name: function() {
                var arabic = [];
                var name = this.get_product().name_arabic;
                arabic.push(name);
                return arabic;
                },
            });

});