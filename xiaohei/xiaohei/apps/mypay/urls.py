from django.conf.urls import url
from mypay import views




urlpatterns = [
    url(r'^wxpay/$',views.wxpay),   #商品
    url(r'^wxpayNotify/$', views.wxpayNotify),
]
