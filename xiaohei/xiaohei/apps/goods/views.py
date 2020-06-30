from django.utils.translation import ugettext_lazy as _
from rest_framework import mixins
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets, filters
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from .models import Goods, GoodsCategory, Banner
from .serializers import GoodsSerializer,GoodsListSerializer,AverseListSerializer, CategorySerializer, ParentCategorySerializer, BannerSerializer, IndexCategoryGoodsSerializer
from .filters import GoodsFilter,GoodsCategoryFilter,GoodsDetailFilter, GoodsSearchFilter
from rest_framework_extensions.cache.mixins import CacheResponseMixin
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class GoodsPagination(PageNumberPagination):
    page_size = 6  # 每一页个数，由于前段
    page_query_description = _('使用分页后的页码')  # 分页文档中文描述
    page_size_query_param = 'page_size'
    page_size_query_description = _('每页返回的结果数')
    page_query_param = 'page'  # 参数?p=xx，将其修改为page，适应前端，也方便识别
    max_page_size = 36  # 最大指定每页个数

'''1 商品分类
分类1 - 分类2 - 商品简要信息
逻辑结构在 serilalizer.py 中
'''
class IndexCategoryGoodsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """

    list:
        商品分类简要信息
    """
    queryset = GoodsCategory.objects.filter(category_type=1)
    serializer_class = IndexCategoryGoodsSerializer




'''2 商品列表搜索 
 (按照商品分类字段'ctype'搜索)额外设置了'cid','name'
 请求参数 'category_type':2
1 获取 商品分类 信息  GoodsCategory
2 反向关联表信息获取 AverseListSerializer
3 调用 过滤器 GoodsCategoryFilter
'''

class GoodsListSearch(CacheResponseMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    list:
        显示商品列表，分页、过滤、搜索、排序
    retrieve:
        显示商品详情
    """
    queryset = GoodsCategory.objects.all()  # 使用get_queryset函数，依赖queryset的值
    # filter
    serializer_class = AverseListSerializer # 商品列表信息
    pagination_class = GoodsPagination      # 分页
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,)  # 将过滤器后端添加到单个视图或视图集
    filterset_class = GoodsCategoryFilter
    # authentication_classes = (TokenAuthentication, )          # 只在本视图中验证Token
    search_fields = ('name','category_id','category_type')      # 搜索字段
     # throttle_classes = [UserRateThrottle, AnonRateThrottle]  # DRF默认限速类，可以仿照写自己的限速类
    throttle_scope = 'goods_list'

    def get_queryset(self):
        keyword = self.request.query_params.get('search')
        if keyword:
            from utils.hotsearch import HotSearch
            hot_search = HotSearch()
            hot_search.save_keyword(keyword)
        return self.queryset


'''3 商品详情
1 构造 过滤器 GoodsDetailFilter
2 'goods_id'字段 匹配页面信息
'''

class GoodsdetailView(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    显示特定的商品详情列表
    """
    queryset = Goods.objects.all()       #用于后台管理的显示
    serializer_class = GoodsSerializer   #用于api的显示

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,)  # 将过滤器后端添加到单个视图或视图集
    filterset_class =  GoodsDetailFilter
    # authentication_classes = (TokenAuthentication, )          # 只在本视图中验证Token
    search_fields = ('name','goods_id')                                # 搜索字段
     # throttle_classes = [UserRateThrottle, AnonRateThrottle]  # DRF默认限速类，可以仿照写自己的限速类
    throttle_scope = 'goods_list'

    def retrieve(self, request, *args, **kwargs):
        # 增加点击数
        instance = self.get_object()
        instance.click_num += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

#--------------------------------------------------------------------------------------------------
'''4 商品模糊搜索  (用作首页商品列表分页)
1 包含两个字段  商品名称name 
             商品简要介绍 goods_brief
'''

class GoodsSearchView(CacheResponseMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    list:
        显示商品列表，分页、过滤、搜索、排序
    retrieve:
        显示商品详情
    """
    queryset = Goods.objects.all()  # 使用get_queryset函数，依赖queryset的值
    # filter
    serializer_class = GoodsListSerializer # 商品列表信息
    pagination_class = GoodsPagination      # 分页
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,)  # 将过滤器后端添加到单个视图或视图集
    filterset_class = GoodsSearchFilter
    # authentication_classes = (TokenAuthentication, )          # 只在本视图中验证Token
    search_fields = ('name','goods_brief')                     # 搜索字段
     # throttle_classes = [UserRateThrottle, AnonRateThrottle]  # DRF默认限速类，可以仿照写自己的限速类
    throttle_scope = 'goods_list'

    def retrieve(self, request, *args, **kwargs):
        # 增加点击数
        instance = self.get_object()
        instance.click_num += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


# ---------------------------------------------------------------------------------------------



class CategoryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    # 注释很有用，在drf文档中
    """
    list:
        商品分类列表

    retrieve:
        商品分类详情
    """
    # queryset = GoodsCategory.objects.all()  # 取出所有分类，没必要分页，因为分类数据量不大
    queryset = GoodsCategory.objects.filter(category_type=1)  # 只获取一级分类数据
    serializer_class = CategorySerializer  # 使用商品类别序列化类，写商品的分类外键已有，直接调用


class ParentCategoryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    list:
        根据子类别查询父类别

    retrieve:
        根据子类别查询父类别详情
    """
    queryset = GoodsCategory.objects.all()
    serializer_class = ParentCategorySerializer


class BannerViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    list:
        获取轮播图列表
    """
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer

# 商品详情总览
class GoodsListView(generics.ListAPIView):
    """
    显示所有的商品详情列表
    """
    queryset = Goods.objects.all()
    serializer_class = GoodsSerializer
    pagination_class = GoodsPagination