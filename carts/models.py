# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from decimal import Decimal
from django.conf import settings
from django.db.models.signals import (
    pre_save,
    post_save,
    post_delete,
)
from django.db import models

from products.models import Variation


class CartItem(models.Model):
    cart = models.ForeignKey("Cart", on_delete=models.CASCADE)
    item = models.ForeignKey(Variation, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField(default=1)
    line_item_total = models.DecimalField(max_digits=20, decimal_places=0)

    def __unicode__(self):
        return self.item.title

    def remove(self):
        return self.item.remove_from_cart()


def cart_item_pre_save_receiver(sender, instance, *args, **kwargs):
    qty = instance.quantity
    if qty >= 1:
        price = instance.item.get_price()
        line_item_total = Decimal(qty) * Decimal(price)
        instance.line_item_total = line_item_total

pre_save.connect(cart_item_pre_save_receiver, sender=CartItem)


def cart_item_post_save_receiver(sender, instance, *args, **kwargs):
    instance.cart.update_subtotal()

post_save.connect(cart_item_post_save_receiver, sender=CartItem)

post_delete.connect(cart_item_post_save_receiver, sender=CartItem)


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)
    items = models.ManyToManyField(Variation, through=CartItem)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    sub_total = models.DecimalField(
        max_digits=20, decimal_places=0, default=10)
    tax_total = models.DecimalField(
        max_digits=20, decimal_places=0, default=10)

    total = models.DecimalField(
        max_digits=20, decimal_places=0, default=10)

    # discount
    # shipping

    def __unicode__(self):
        return str(self.id)

    def update_subtotal(self):
        sub_total = 0
        items = self.cartitem_set.all()
        for item in items:
            sub_total += item.line_item_total

        self.sub_total = sub_total
        self.save()


def do_tax_and_total_receiver(sender, instance, *args, **kwargs):
    sub_total = instance.sub_total
    tax_total = round(sub_total * Decimal(settings.TAX_PERCENTAGE))
    tax_total = int(tax_total)
    total = sub_total + tax_total
    instance.tax_total = tax_total
    instance.total = total

pre_save.connect(do_tax_and_total_receiver, sender=Cart)
