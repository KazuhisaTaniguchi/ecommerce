# -*- coding: utf-8 -*-
from django.db.models import Q
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
# from django.shortcuts import render, get_object_or_404
# from django.utils import timezone

from .models import Product


class ProductListView(ListView):
    model = Product

    def get_context_data(self, *args, **kwargs):
        context = super(
            ProductListView, self).get_context_data(*args, **kwargs)
        # context["now"] = timezone.now()
        context['query'] = self.request.GET.get('q')
        return context

    def get_queryset(self, *args, **kwargs):
        qs = super(ProductListView, self).get_queryset(*args, **kwargs)
        query = self.request.GET.get('q')
        if query:
            qs = self.model.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query),
            )
            try:
                qs2 = self.model.objects.filter(
                    Q(price=query)
                )
                qs = (qs | qs2).distinct()
            except:
                pass
        return qs


class ProductDetailView(DetailView):
    model = Product


# def product_detail_view_func(request, id):
#     product_instance = get_object_or_404(Product, id=id)
#     template = 'products/product_detail.html'
#     context = {
#         'object': product_instance,
#     }
#     return render(request, template, context)
