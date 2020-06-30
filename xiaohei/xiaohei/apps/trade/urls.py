"""xiaohei URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from trade.views import OrderInfoViewSet,ShoppingCartViewSet,AliPayView,AliPayView2
#
router = DefaultRouter()
router.register(r'tradeCart', OrderInfoViewSet, basename='tradeCart')  # 订单信息
router.register(r'ShopCart', ShoppingCartViewSet, basename='ShoppingCart')  # 购物车
router.register(r'AliPay', AliPayView, basename='AliPay')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^ShoppingCart/$', ShoppingCartViewSet.as_view({'get': 'list'}),name='cartList' ),  # 登录
    # url('^AliPay/$', AliPayView.as_view(), name='AliPay'),  # 用户
    url(r'alipay/return/$',AliPayView2.as_view(),name='alipay')
]
