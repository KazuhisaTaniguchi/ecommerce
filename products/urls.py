from django.conf.urls import url
from .views import ProductDetailView

urlpatterns = [
    url(r'^(?P<pk>\d+)',
        ProductDetailView.as_view(), name='product_detail'),
]
