# -*- coding: utf-8 -*-
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse
from django.http import Http404, JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect

from django.views.generic.base import View
from django.views.generic.detail import SingleObjectMixin, DetailView
from django.views.generic.edit import FormMixin

from orders.mixins import CartOrderMixin
from orders.forms import GuestCheckoutForm

from products.models import Variation
from .models import Cart, CartItem
from orders.models import UserCheckout, Order, UserAddress


class ItemCountView(View):

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            cart_id = self.request.session.get("cart_id")
            count = 0

            if cart_id is None:
                count = 0
            else:
                cart = get_object_or_404(Cart, id=cart_id)
                count = cart.items.count()

            request.session['cart_item_count'] = count

            return JsonResponse({'count': count})
        else:
            return Http404


class CartView(SingleObjectMixin, View):
    model = Cart
    template_name = 'carts/view.html'

    def get_object(self, *args, **kwargs):
        # 300 is 5 minutes
        # 0 is closeing Browser
        self.request.session.set_expiry(0)
        cart_id = self.request.session.get("cart_id")
        if cart_id is None:
            # cart = Cart()
            cart = Cart.objects.create()
            cart.save()
            cart_id = cart.id
            self.request.session['cart_id'] = cart_id
        cart = Cart.objects.get(id=cart_id)

        if self.request.user.is_authenticated():
            cart.user = self.request.user
            cart.save()
        return cart

    def get(self, request, *args, **kwargs):
        cart = self.get_object()

        item_id = request.GET.get('item')
        delete_item = request.GET.get('delete', False)
        flash_message = ''
        item_added = False

        if item_id:
            item_instance = get_object_or_404(Variation, id=item_id)
            qty = request.GET.get('qty', 1)
            try:
                if int(qty) < 1:
                    delete_item = True
            except:
                raise Http404
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart, item=item_instance)

            if created:
                flash_message = 'カートに追加されました｡'
                item_added = True

            if delete_item:
                flash_message = 'カートから移動しました｡'
                cart_item.delete()
            else:
                if not created:
                    flash_message = '商品数を変更しました｡'

                cart_item.quantity = qty
                cart_item.save()

            if not request.is_ajax():
                return HttpResponseRedirect(reverse('cart'))

        if request.is_ajax():
            try:
                total = cart_item.line_item_total
            except:
                total = None

            try:
                subtotal = cart_item.cart.sub_total
            except:
                subtotal = None

            try:
                tax_total = cart_item.cart.tax_total
            except:
                tax_total = 0

            try:
                cart_total = cart_item.cart.total
            except:
                cart_total = 0

            try:
                total_items = cart_item.cart.items.count()
            except:
                total_items = 0

            ajax_data = {
                'deleted': delete_item,
                'item_added': item_added,
                'line_total': total,
                'subtotal': subtotal,
                'tax_total': tax_total,
                'cart_total': cart_total,
                'flash_message': flash_message,
                'total_items': total_items,
            }
            return JsonResponse(ajax_data)

        context = {
            'object': self.get_object()
        }
        template = self.template_name
        return render(request, template, context)


class CheckoutView(CartOrderMixin, FormMixin, DetailView):
    model = Cart
    template_name = 'carts/checkout_view.html'
    form_class = GuestCheckoutForm

    def get_object(self, *args, **kwargs):

        cart = self.get_cart()
        if cart is None:
            return None

        return cart

    def get_context_data(self, *args, **kwargs):
        context = super(CheckoutView, self).get_context_data(*args, **kwargs)

        user_can_continue = False

        user_check_id = self.request.session.get('user_checkout_id')

        if self.request.user.is_authenticated():
            user_can_continue = True

            user_checkout, created = UserCheckout.objects.get_or_create(
                email=self.request.user.email)

            user_checkout.user = self.request.user
            user_checkout.save()

            self.request.session['user_checkout_id'] = user_checkout.id
        elif (not self.request.user.is_authenticated() and
                user_check_id is None):

            context['login_form'] = AuthenticationForm()
            context['next_url'] = self.request.build_absolute_uri()
        else:
            pass

        if user_check_id is not None:
            user_can_continue = True

        context['order'] = self.get_order()

        context['user_can_continue'] = user_can_continue
        context['form'] = self.get_form()
        return context

    def post(self, request, *args, **kwargs):
        # assign the object to the view
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            email = form.cleaned_data.get("email")
            user_checkout, created = UserCheckout.objects.get_or_create(
                email=email)
            request.session['user_checkout_id'] = user_checkout.id

            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse("checkout")

    def get(self, request, *args, **kwargs):
        get_data = super(CheckoutView, self).get(request, *args, **kwargs)

        cart = self.get_object()
        if cart is None:
            return redirect('cart')

        new_order = self.get_order()

        user_checkout_id = request.session.get('user_checkout_id')
        if user_checkout_id is not None:

            user_checkout = UserCheckout.objects.get(id=user_checkout_id)

            if (new_order.billing_address is None or
                    new_order.shipping_address is None):

                    return redirect('order_address')

            new_order.user = user_checkout

            new_order.save()

        return get_data


class CheckoutFinalView(CartOrderMixin, View):

    def post(self, request, *args, **kwargs):
        order = self.get_order()
        if request.POST.get('payment_token') == 'ABC':
            order.mark_completed()
            messages.success(request, 'ご注文ありがとうございます。')
            del request.session['cart_id']
            del request.session['order_id']
        return redirect('order_detail', pk=order.pk)

    def get(self, request, *args, **kwargs):
        return redirect('checkout')
