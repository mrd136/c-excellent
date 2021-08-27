odoo.define("sh_pos_access_rights.screens", function (require) {
    "use strict";

    const ActionpadWidget = require("point_of_sale.ActionpadWidget");
    const NumpadWidget = require("point_of_sale.NumpadWidget");
    const PaymentScreen = require("point_of_sale.PaymentScreen");

    const Registries = require("point_of_sale.Registries");

    const { useBarcodeReader } = require("point_of_sale.custom_hooks");
    const { useListener } = require("web.custom_hooks");
    var models = require("point_of_sale.models");
    var core = require("web.core");
    var rpc = require("web.rpc");
    var Session = require("web.session");

    var QWeb = core.qweb;
    var _t = core._t;

    const SHPaymentScreen = (PaymentScreen) =>
        class extends PaymentScreen {
            mounted() {
                super.mounted();
                var self = this;
                _.each(this.env.pos.users, function (user) {
                    if (user["id"] == self.env.pos.get_cashier().user_id[0]) {
                        // Enable-disable customer selection Button
                        if (user.groups_id.indexOf(self.env.pos.config.group_select_customer[0]) === -1) {
                            $(".customer-button").prop("disabled", false);
                            $(".customer-button").removeClass("sh_disabled");
                        } else {
                            $(".customer-button").prop("disabled", true);
                            $(".customer-button").addClass("sh_disabled");
                        }
                    }
                });
            }
        };
    Registries.Component.extend(PaymentScreen, SHPaymentScreen);

    const SHNumpadWidget = (NumpadWidget) =>
        class extends NumpadWidget {
            mounted() {
                var self = this;
                super.mounted(...arguments);
                _.each(self.env.pos.users, function (user) {
                    if (user["id"] == self.env.pos.get_cashier().user_id[0]) {
                        // Enable-disable discount Button
                        if (user.groups_id.indexOf(self.env.pos.config.group_disable_discount[0]) === -1) {
                            $($(".mode-button")[1]).prop("disabled", false);
                            $($(".mode-button")[1]).removeClass("sh_disabled_qty");
                        } else {
                            $($(".mode-button")[1]).prop("disabled", true);
                            $($(".mode-button")[1]).addClass("sh_disabled_qty");
                        }
                        // Enable-disable qty Button
                        if (user.groups_id.indexOf(self.env.pos.config.group_disable_qty[0]) === -1) {
                            $($(".mode-button")[0]).prop("disabled", false);
                            $($(".mode-button")[0]).removeClass("sh_disabled_qty");
                        } else {
                            $($(".mode-button")[0]).prop("disabled", true);
                            $($(".mode-button")[0]).addClass("sh_disabled_qty");
                        }
                        // Enable-disable price Button
                        if (user.groups_id.indexOf(self.env.pos.config.group_disable_price[0]) === -1) {
                            $($(".mode-button")[2]).prop("disabled", false);
                            $($(".mode-button")[2]).removeClass("sh_disabled_qty");
                        } else {
                            $($(".mode-button")[2]).prop("disabled", true);
                            $($(".mode-button")[2]).addClass("sh_disabled_qty");
                        }
                        // Enable-disable Plus Minus
                        if (user.groups_id.indexOf(self.env.pos.config.group_disable_plus_minus[0]) === -1) {
                            $(".numpad-minus").prop("disabled", false);
                            $(".numpad-minus").removeClass("sh_disabled");
                        } else {
                            $(".numpad-minus").prop("disabled", true);
                            $(".numpad-minus").addClass("sh_disabled");
                        }
                        // Enable-disable Numpad
                        if (user.groups_id.indexOf(self.env.pos.config.group_disable_numpad[0]) === -1) {
                            $(".number-char").prop("disabled", false);
                            $(".number-char").removeClass("sh_disabled");
                        } else {
                            $(".number-char").prop("disabled", true);
                            $(".number-char").addClass("sh_disabled");
                        }
                    }
                });
                this.changeMode("quantity");
            }
            changeMode(mode) {
                super.changeMode(...arguments);

                if (this.env.pos.user.groups_id.indexOf(this.env.pos.config.group_disable_qty[0]) != -1 && this.env.pos.user.groups_id.indexOf(this.env.pos.config.group_disable_price[0]) != -1) {
                    mode = "discount";
                    this.trigger("set-numpad-mode", { mode });
                    this.props.activeMode = "discount";
                } else if (this.env.pos.user.groups_id.indexOf(this.env.pos.config.group_disable_qty[0]) != -1) {
                    mode = "price";
                    this.trigger("set-numpad-mode", { mode });
                    this.props.activeMode = "price";
                }
            }
        };

    Registries.Component.extend(NumpadWidget, SHNumpadWidget);

    const SHActionpadWidget = (ActionpadWidget) =>
        class extends ActionpadWidget {
            mounted() {
                super.mounted(...arguments);
                var self = this;
                _.each(this.env.pos.users, function (user) {
                    if (user["id"] == self.env.pos.get_cashier().user_id[0]) {
                        // Enable-disable Payment Button
                        if (user.groups_id.indexOf(self.env.pos.config.disable_payment_id[0]) === -1) {
                            $(".pay").prop("disabled", false);
                            $(".pay").removeClass("sh_disabled");
                        } else {
                            $(".pay").prop("disabled", true);
                            $(".pay").addClass("sh_disabled");
                        }
                        // Enable-disable customer selection Button
                        if (user.groups_id.indexOf(self.env.pos.config.group_select_customer[0]) === -1) {
                            $(".set-customer").prop("disabled", false);
                            $(".set-customer").removeClass("sh_disabled");
                        } else {
                            $(".set-customer").prop("disabled", true);
                            $(".set-customer").addClass("sh_disabled");
                        }
                    }
                });
            }
        };

    Registries.Component.extend(ActionpadWidget, SHActionpadWidget);

    return {
        NumpadWidget,
        ActionpadWidget,
    };
});
