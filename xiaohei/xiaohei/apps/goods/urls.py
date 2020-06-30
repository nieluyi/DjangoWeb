"""xiaohei URL Configuration
注册resful格式的url，resful格式的api的管理
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

from goods.views import GoodsListView,GoodsListSearch,CategoryViewSet, ParentCategoryViewSet,BannerViewSet,\
    IndexCategoryGoodsViewSet,GoodsdetailView,GoodsSearchView

router = DefaultRouter()#router的作用就是将viewset对象的url映射关系提取出来
#将定义的View方法提取出来
router.register(r'GoodsListSearch', GoodsListSearch, basename='GoodsListSearch')  #商品简要信息列表
router.register(r'CategoryViewSet', CategoryViewSet, basename='SearchAllDateViewSet') #商品分类
router.register(r'ParentCategoryViewSet',ParentCategoryViewSet, basename='MapModelAllDateViewSet')#
router.register(r'BannerViewSet', BannerViewSet, basename='BannerView') #轮播图
router.register(r'IndexCategoryGoodsViewSet', IndexCategoryGoodsViewSet, basename='RegistrationAllDataViewSet')
router.register(r'GoodsdetailView', GoodsdetailView, basename='GoodsdetailView') #商品详情
router.register(r'GoodsSearch', GoodsSearchView, basename='GoodsSearchView') #商品搜索

urlpatterns = [
    url(r'^', include(router.urls)),    #显示所有的urls概览也就是显示下面这个的框框
    url(r'^GoodsListView/$', GoodsListView.as_view(), name='GoodsListView'),  # 商品详情
    #as_view()用于注册没有view_set的视图  即传入参数中没有viewsets.GenericViewSet
]
