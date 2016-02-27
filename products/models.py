# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save
# from django.utils.text import slugify
from django.utils.text import mark_safe


class ProductQuerySet(models.query.QuerySet):
    def active(self):
        return self.filter(active=True)


class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

    def all(self, *args, **kwargs):
        return self.get_queryset().active()

    def get_related(self, instance):
        product_one = self.get_queryset().filter(
            categories__in=instance.categories.all(),
            # categories__in__exact=instance.categories.all(),
        )
        product_two = self.get_queryset().filter(
            default=instance.default,
        )
        product_list = (product_one | product_two).exclude(
            id=instance.id).distinct()

        return product_list


class Product(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(
        decimal_places=0,
        max_digits=20,
    )
    active = models.BooleanField(default=True)
    categories = models.ManyToManyField('Category', blank=True)
    default = models.ForeignKey(
        'Category', related_name='default_category', null=True, blank=True)

    objects = ProductManager()

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("products:product_detail", kwargs={"pk": self.pk})

    def get_image_url(self):
        img = self.productimage_set.first()
        if img:
            return img.image.url
        return img


class Variation(models.Model):
    product = models.ForeignKey(Product)
    title = models.CharField(max_length=120)
    price = models.DecimalField(
        decimal_places=0,
        max_digits=20,
    )
    sale_price = models.DecimalField(
        decimal_places=0,
        max_digits=20,
        null=True,
        blank=True,
    )
    active = models.BooleanField(default=True)
    inventory = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return self.title

    def get_price(self):
        if self.sale_price is not None:
            return self.sale_price
        else:
            return self.price

    def get_html_price(self):
        if self.sale_price is not None:
            html_text = "<span class='sale-price'>%s </span>" % (
                self.sale_price)

            html_text += "<span class='og-price'>%s</span>" % (self.price)
        else:
            html_text = "<span class='price'>%s</span>" % (self.price)

        return mark_safe(html_text)

    def get_absolute_url(self):
        return self.product.get_absolute_url()

    def add_to_cart(self):
        return '%s?item=%s&qty=1' % (
            reverse('cart'),
            self.id,
        )

    def remove_from_cart(self):
        return '%s?item=%s&qty=1&delete=True' % (
            reverse('cart'),
            self.id
            )

    def get_title(self):
        return '%s - %s' % (self.product.title, self.title)


def product_post_save_receiver(sender, instance, created, *args, **kwargs):
    product = instance
    variations = product.variation_set.all()
    if variations.count() == 0:
        new_var = Variation()
        new_var.product = product
        new_var.title = 'Default'
        new_var.price = product.price
        new_var.save()

post_save.connect(product_post_save_receiver, sender=Product)


def image_upload_to(instance, filename):
    title = instance.product.title
    # slug = slugify(title)
    return 'products/%s/%s' % (title, filename)


class ProductImage(models.Model):
    product = models.ForeignKey(Product)
    image = models.ImageField(upload_to=image_upload_to)

    def __unicode__(self):
        return self.product.title


class Category(models.Model):
    title = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    description = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
            'categories:category_detail', kwargs={'slug': self.slug})


def image_upload_to_featured(instance, filename):
    title = instance.product.title
    return 'products/%s/featured/%s' % (title, filename)


class ProductFeatured(models.Model):
    product = models.ForeignKey(Product)
    image = models.ImageField(upload_to=image_upload_to_featured)
    title = models.CharField(max_length=120, null=True, blank=True)
    text = models.CharField(max_length=220, null=True, blank=True)
    text_right = models.BooleanField(default=False)
    text_css_color = models.CharField(max_length=6, null=True, blank=True)
    show_price = models.BooleanField(default=False)
    make_image_background = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.product.title
