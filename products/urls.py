from django.conf.urls import url
from .views import (
    ProductDetailView,
    ProductListView,
    VariationListView,
    product_list,
)

urlpatterns = [
    # url(r'^$', product_list, name='products'),
    url(r'^$', ProductListView.as_view(), name='products'),
    url(r'^(?P<pk>\d+)$',
        ProductDetailView.as_view(), name='product_detail'),
    url(r'^(?P<pk>\d+)/inventory$',
        VariationListView.as_view(), name='variations'),
]
