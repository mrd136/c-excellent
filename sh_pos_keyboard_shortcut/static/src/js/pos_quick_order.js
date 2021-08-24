odoo.define("sh_pos_keyboard_shortcut.sh_quick_order", function (require) {
    "use strict";

    var models = require("point_of_sale.models");
    var DB = require("point_of_sale.DB");
    var screens = require("point_of_sale.screens");
    var gui = require("point_of_sale.gui");
    var PopupWidget = require("point_of_sale.popups");

    DB.include({
        init: function (options) {
            this._super(options);
            this.all_key = [];
            this.all_key_screen = [];
            this.key_screen_by_id = {};
            this.key_by_id = {};
            this.screen_by_key = {};
            this.keysPressed = {};
            this.pressedKeyList = [];
            this.key_screen_by_grp = {};
            this.key_payment_screen_by_grp = {};
            this.temp_key_by_id = {};
        },
    });

    models.load_models({
        model: "sh.keyboard.key",
        fields: ["name"],
        loaded: function (self, keys) {
            self.db.all_key = keys;
            _.each(keys, function (each_key) {
                if (each_key && each_key.name) {
                    self.db.key_by_id[each_key["id"]] = each_key;
                }
            });
        },
    });

    models.load_models({
        model: "sh.keyboard.key.temp",
        fields: ["name", "sh_key_ids"],
        loaded: function (self, keys) {
            self.db.all_key = keys;
            _.each(keys, function (each_key) {
                if (each_key && each_key.name) {
                    self.db.temp_key_by_id[each_key["id"]] = each_key;
                }
            });
        },
    });

    models.load_models({
        model: "sh.pos.keyboard.shortcut",
        fields: ["sh_key_ids", "sh_shortcut_screen", "config_id", "payment_method_id", "sh_payment_shortcut_screen_type", "sh_shortcut_screen_type"],
        loaded: function (self, keys) {
            self.db.all_key_screen = keys;
            _.each(keys, function (each_key_data) {
                var key_combine = "";
                _.each(each_key_data["sh_key_ids"], function (each_key) {
                    if (key_combine != "") {
                        key_combine = key_combine + "+" + self.db.temp_key_by_id[each_key]["sh_key_ids"][1];
                    } else {
                        key_combine = self.db.temp_key_by_id[each_key]["sh_key_ids"][1];
                    }
                });

                if (each_key_data.payment_method_id && each_key_data.payment_method_id[1]) {
                    self.db.screen_by_key[key_combine] = each_key_data["payment_method_id"][0];
                    self.db.key_screen_by_id[each_key_data["payment_method_id"][1]] = key_combine;
                    if (each_key_data["sh_payment_shortcut_screen_type"]) {
                        if (self.db.key_payment_screen_by_grp[each_key_data["sh_payment_shortcut_screen_type"]]) {
                            self.db.key_payment_screen_by_grp[each_key_data["sh_payment_shortcut_screen_type"]].push(each_key_data["payment_method_id"][1]);
                        } else {
                            self.db.key_payment_screen_by_grp[each_key_data["sh_payment_shortcut_screen_type"]] = [each_key_data["payment_method_id"][1]];
                        }
                    }
                } else {
                    self.db.key_screen_by_id[each_key_data["sh_shortcut_screen"]] = key_combine;
                    if (each_key_data.sh_shortcut_screen_type) {
                        if (self.db.key_screen_by_grp[each_key_data.sh_shortcut_screen_type]) {
                            self.db.key_screen_by_grp[each_key_data.sh_shortcut_screen_type].push(each_key_data["sh_shortcut_screen"]);
                        } else {
                            self.db.key_screen_by_grp[each_key_data.sh_shortcut_screen_type] = [each_key_data["sh_shortcut_screen"]];
                        }
                    }
                }
            });
        },
    });

    document.addEventListener("keydown", (event) => {
        self.posmodel.db.keysPressed[event.key] = true;
    });

    document.addEventListener("keyup", (event) => {
        delete self.posmodel.db.keysPressed[event.key];
    });

    document.addEventListener("keydown", (event) => {
        if (self.posmodel.config.sh_enable_shortcut) {
            self.posmodel.db.keysPressed[event.key] = true;
            self.posmodel.db.pressedKeyList = [];
            for (var key in self.posmodel.db.keysPressed) {
                if (self.posmodel.db.keysPressed[key]) {
                    self.posmodel.db.pressedKeyList.push(key);
                }
            }
            if (self.posmodel.db.pressedKeyList.length > 0) {
                var pressed_key = "";
                for (var i = 0; i < self.posmodel.db.pressedKeyList.length > 0; i++) {
                    if (self.posmodel.db.pressedKeyList[i]) {
                        if (pressed_key != "") {
                            pressed_key = pressed_key + "+" + self.posmodel.db.pressedKeyList[i];
                        } else {
                            pressed_key = self.posmodel.db.pressedKeyList[i];
                        }
                    }
                }
                if ($(".payment-screen").is(":visible")) {
                    if (self.posmodel.db.screen_by_key[pressed_key]) {
                        event.preventDefault();
                        self.posmodel.gui.screen_instances.payment.click_paymentmethods(self.posmodel.db.screen_by_key[pressed_key]);
                    }
                }
                for (var key in self.posmodel.db.key_screen_by_id) {
                    if (self.posmodel.db.key_screen_by_id[key] == pressed_key) {
                        if (!$(".searchbox input").is(":focus")) {
                            if (key == "select_up_orderline") {
                                event.preventDefault();
                                event.stopPropagation();
                                if ($(".product-screen").is(":visible")) {
                                    $(document).find("div.product-screen ul.orderlines li.selected").prev("li.orderline").trigger("click");
                                }
                            } else if (key == "select_down_orderline") {
                                event.preventDefault();
                                event.stopPropagation();
                                if ($(".product-screen").is(":visible")) {
                                    $(document).find("div.product-screen ul.orderlines li.selected").next("li.orderline").trigger("click");
                                }
                            } else if (key == "select_up_customer") {
                                if ($(document).find("div.clientlist-screen table.client-list tbody.client-list-contents tr.highlight").length > 0) {
                                    $(document).find("div.clientlist-screen table.client-list tbody.client-list-contents tr.highlight").prev("tr.client-line").click();
                                } else {
                                    var clientLineLength = $(document).find("div.clientlist-screen table.client-list tbody.client-list-contents tr.client-line").length;
                                    if (clientLineLength > 0) {
                                        $($(document).find("div.clientlist-screen table.client-list tbody.client-list-contents tr.client-line")[clientLineLength - 1]).click();
                                    }
                                }
                            } else if (key == "select_down_customer") {
                                if ($(document).find("div.clientlist-screen table.client-list tbody.client-list-contents tr.highlight").length > 0) {
                                    $(document).find("div.clientlist-screen table.client-list tbody.client-list-contents tr.highlight").next("tr.client-line").click();
                                } else {
                                    var clientLineLength = $(document).find("div.clientlist-screen table.client-list tbody.client-list-contents tr.client-line").length;
                                    if (clientLineLength > 0) {
                                        $($(document).find("div.clientlist-screen table.client-list tbody.client-list-contents tr.client-line")[0]).click();
                                    }
                                }
                            } else if (key == "go_payment_screen") {
                                event.preventDefault();
                                event.stopPropagation();
                                if ($(".product-screen").is(":visible")) {
                                    $(".pay").trigger("click");
                                }
                            } else if (key == "go_customer_Screen") {
                                event.preventDefault();
                                event.stopPropagation();
                                if ($(".product-screen").is(":visible") || $(".payment-screen").is(":visible")) {
                                    $(".set-customer").trigger("click");
                                }
                            } else if (key == "validate_order") {
                                event.preventDefault();
                                event.stopPropagation();
                                if ($(".payment-screen").is(":visible")) {
                                    self.posmodel.gui.screen_instances.payment.validate_order();
                                }
                            } else if (key == "next_order") {
                                event.preventDefault();
                                event.stopPropagation();
                                if ($(".receipt-screen").is(":visible")) {
                                    self.posmodel.gui.screen_instances.receipt.click_next();
                                }
                            } else if (key == "go_to_previous_screen") {
                                event.preventDefault();
                                event.stopPropagation();
                                if (!$(".product-screen").is(":visible") && !$(".receipt-screen").is(":visible")) {
                                    $(".back").trigger("click");
                                }
                            } else if (key == "select_quantity_mode") {
                                event.preventDefault();
                                event.stopPropagation();
                                if ($(".product-screen").is(":visible")) {
                                    if ($('.mode-button[data-mode="quantity"]')) {
                                        $('.mode-button[data-mode="quantity"]').click();
                                    }
                                }
                            } else if (key == "select_discount_mode") {
                                event.preventDefault();
                                event.stopPropagation();
                                if ($(".product-screen").is(":visible")) {
                                    if ($('.mode-button[data-mode="discount"]')) {
                                        $('.mode-button[data-mode="discount"]').click();
                                    }
                                }
                            } else if (key == "select_price_mode") {
                                event.preventDefault();
                                event.stopPropagation();
                                if ($(".product-screen").is(":visible")) {
                                    if ($('.mode-button[data-mode="price"]')) {
                                        $('.mode-button[data-mode="price"]').click();
                                    }
                                }
                            } else if (key == "search_product") {
                                event.preventDefault();
                                event.stopPropagation();
                                if ($(".product-screen").is(":visible")) {
                                    $(".searchbox input").focus();
                                    $(".search-clear").click();
                                }
                            } else if (key == "add_new_order") {
                                event.preventDefault();
                                event.stopPropagation();
                                self.posmodel.add_new_order();
                            } else if (key == "destroy_current_order") {
                                event.preventDefault();
                                event.stopPropagation();
                                $(".deleteorder-button").click();
                            } else if (key == "delete_orderline") {
                                if ($(".product-screen").is(":visible")) {
                                    if (self.posmodel.get_order().get_selected_orderline()) {
                                        setTimeout(function () {
                                            self.posmodel.get_order().remove_orderline(self.posmodel.get_order().get_selected_orderline());
                                        }, 100);
                                    }
                                }
                            } else if (key == "search_customer") {
                                event.preventDefault();
                                event.stopPropagation();
                                if ($(".clientlist-screen").is(":visible")) {
                                    $(".searchbox input").focus();
                                    $(".search-clear").click();
                                }
                            } else if (key == "set_customer") {
                                event.preventDefault();
                                event.stopPropagation();
                                if ($(".clientlist-screen").is(":visible")) {
                                    if (!$(document).find("div.clientlist-screen section.top-content span.next").hasClass("oe_hidden")) {
                                        $(document).find("div.clientlist-screen section.top-content span.next").click();
                                    }
                                }
                            } else if (key == "create_customer") {
                                event.preventDefault();
                                event.stopPropagation();
                                if ($(".clientlist-screen").is(":visible")) {
                                    $(document).find("div.clientlist-screen section.top-content span.new-customer").click();
                                    $(document).find("div.clientlist-screen section.full-content section.client-details input.client-name").focus();
                                }
                            } else if (key == "save_customer") {
                                if (!$(document.activeElement).is(":focus")) {
                                    event.preventDefault();
                                    event.stopPropagation();
                                    if ($(".clientlist-screen").is(":visible")) {
                                        $(document).find("div.clientlist-screen section.full-content div.edit-buttons div.save i.fa-floppy-o").click();
                                    }
                                }
                            } else if (key == "edit_customer") {
                                if (!$(document.activeElement).is(":focus")) {
                                    event.preventDefault();
                                    event.stopPropagation();
                                    if ($(".clientlist-screen").is(":visible")) {
                                        $(document).find("div.clientlist-screen section.full-content div.edit-buttons div.edit i.fa-pencil-square").click();
                                        $(document).find("div.clientlist-screen section.full-content section.client-details input.client-name").focus();
                                    }
                                }
                            } else if (key == "undo_customer_detail") {
                                if (!$(document.activeElement).is(":focus")) {
                                    event.preventDefault();
                                    event.stopPropagation();
                                    if ($(".clientlist-screen").is(":visible")) {
                                        $(document).find("div.clientlist-screen section.full-content div.edit-buttons div.undo i.fa-undo").click();
                                    }
                                }
                            } else if (key == "select_up_payment_line") {
                                if ($(".payment-screen").is(":visible")) {
                                    if ($($(document).find("div.payment-screen")[0]).find("tr.paymentline.selected").length > 0) {
                                        var elem = $($(document).find("div.payment-screen")[0]).find("tr.paymentline.selected");
                                        if (elem.prev("tr.paymentline").length > 0) {
                                            self.posmodel.gui.screen_instances.payment.click_paymentline(elem.prev("tr.paymentline").data("cid"));
                                        }
                                    }
                                }
                            } else if (key == "select_down_payment_line") {
                                if ($(".payment-screen").is(":visible")) {
                                    if ($($(document).find("div.payment-screen")[0]).find("tr.paymentline.selected").length > 0) {
                                        var elem = $($(document).find("div.payment-screen")[0]).find("tr.paymentline.selected");
                                        if (elem.next("tr.paymentline").length > 0 && !elem.next("tr.paymentline").hasClass("extra")) {
                                            self.posmodel.gui.screen_instances.payment.click_paymentline(elem.next("tr.paymentline").data("cid"));
                                        }
                                    }
                                }
                            } else if (key == "delete_payment_line") {
                                if ($(".payment-screen").is(":visible")) {
                                    event.preventDefault();
                                    var elem = $($(document).find("div.payment-screen")[0]).find("tr.paymentline.selected");
                                    if (elem.next("tr.paymentline").length > 0 && !elem.next("tr.paymentline").hasClass("extra")) {
                                        $($(document).find("div.payment-screen")[0]).find("table.paymentlines tbody tr.selected td.delete-button").trigger("click");
                                        self.posmodel.gui.screen_instances.payment.click_paymentline(elem.next("tr.paymentline").data("cid"));
                                    } else {
                                        var elem = $($(document).find("div.payment-screen")[0]).find("tr.paymentline.selected");
                                        $($(document).find("div.payment-screen")[0]).find("table.paymentlines tbody tr.selected td.delete-button").trigger("click");
                                        if (elem.prev("tr.paymentline").length > 0) {
                                            self.posmodel.gui.screen_instances.payment.click_paymentline(elem.prev("tr.paymentline").data("cid"));
                                        }
                                    }
                                }
                            } else if (key == "+10") {
                                if ($(".payment-screen").is(":visible")) {
                                    if ($('.mode-button[data-action="+10"]')) {
                                        self.posmodel.gui.screen_instances.payment.click_numpad($($('.mode-button[data-action="+10"]')[0]));
                                    }
                                }
                            } else if (key == "+20") {
                                if ($(".payment-screen").is(":visible")) {
                                    if ($('.mode-button[data-action="+20"]')) {
                                        self.posmodel.gui.screen_instances.payment.click_numpad($($('.mode-button[data-action="+20"]')[0]));
                                    }
                                }
                            } else if (key == "+50") {
                                if ($(".payment-screen").is(":visible")) {
                                    if ($('.mode-button[data-action="+50"]')) {
                                        self.posmodel.gui.screen_instances.payment.click_numpad($($('.mode-button[data-action="+50"]')[0]));
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    });

    document.addEventListener("keyup", (event) => {
        delete self.posmodel.db.keysPressed[event.key];
    });

    var SeeShortcutButton = screens.ActionButtonWidget.extend({
        template: "SeeShortcutButton",
        button_click: function () {
            this.pos.gui.show_popup("shortcut_tips_popup");
        },
    });

    screens.define_action_button({
        name: "shortcut_tips",
        widget: SeeShortcutButton,
        condition: function () {
            return this.pos.config.sh_enable_shortcut;
        },
    });

    var ShortCutListPopupWidget = PopupWidget.extend({
        template: "ShortCutListPopupWidget",
        show: function (options) {
            options = options || {};
            this._super(options);
        },
    });

    gui.define_popup({
        name: "shortcut_tips_popup",
        widget: ShortCutListPopupWidget,
    });
});
