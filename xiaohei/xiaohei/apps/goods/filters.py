from django_filters import rest_framework as filters
from django.db.models import Q
from .models import Goods,GoodsCategory


class GoodsFilter(filters.FilterSet):
    """
    商品的过滤类
    """
    name = filters.CharFilter(field_name='name', lookup_expr='contains', help_text='分类名模糊匹配')  # 包含关系，模糊匹配
    goods_desc = filters.CharFilter(field_name='name', lookup_expr='contains', help_text='商品描述模糊匹配')
    min_price = filters.NumberFilter(field_name="shop_price", lookup_expr='gte', help_text='最低价格')  # 自定义字段
    max_price = filters.NumberFilter(field_name="shop_price", lookup_expr='lte', help_text='最高价格')
    top_category = filters.NumberFilter(method='top_category_filter', field_name='category_id', lookup_expr='=', help_text='自定义过滤某个一级分类')  # 自定义过滤，过滤某个一级分类
    goods_id =filters.NumberFilter(method='top_category_filter', field_name='id', lookup_expr='=', help_text='搜寻货物id')  # 自定义过滤，过滤某个一级分类

    def top_category_filter(self, queryset, field_name, value):
        """
        自定义过滤内容
        这儿是传递一个分类的id，在已有商品查询集基础上获取分类id，一级一级往上找，直到将三级类别找完
        :param queryset:
        :param field_name:
        :param value: 需要过滤的值
        :return:
        """
        queryset = queryset.filter(Q(category_id=value) | Q(category__parent_category_id=value) | Q(category__parent_category__parent_category_id=value))
        return queryset

    class Meta:
        model = Goods
        fields = ['name','goods_id','goods_desc', 'min_price', 'max_price', 'category_id','is_hot', 'is_new']

'''商品列表 过滤
1 过滤字段为 name category_id category_type
'''
class GoodsCategoryFilter(filters.FilterSet):
    """
    商品的过滤类
    """
    name = filters.CharFilter(field_name='name', lookup_expr='contains', help_text='分类名')  # 包含关系，模糊匹配
    category_id = filters.NumberFilter(field_name="category_id", lookup_expr='=', help_text='分类id')  # 自定义字段
    category_type = filters.NumberFilter(field_name="category_type", lookup_expr='=', help_text='分类类型')

    def top_category_filter(self, queryset, field_name, value):
        """
        自定义过滤内容
        这儿是传递一个分类的id，在已有商品查询集基础上获取分类id，一级一级往上找，直到将三级类别找完
        :param queryset:
        :param field_name:
        :param value: 需要过滤的值
        :return:
        """
        queryset = queryset.filter(Q(category_id=value) | Q(category__parent_category_id=value) | Q(category__parent_category__parent_category_id=value))
        return queryset

    class Meta:
        model = GoodsCategory
        fields = ['name','category_id','category_type']

'''商品详细信息 过滤
1 过滤字段为 goods_id
'''
class GoodsDetailFilter(filters.FilterSet):
    """
    商品的过滤类
    """
    name = filters.CharFilter(field_name='name', lookup_expr='contains', help_text='商品名')  # 包含关系，模糊匹配
    goods_id = filters.NumberFilter(field_name="goods_id", lookup_expr='contains', help_text='商品id')  # 自定义字段

    class Meta:
        model = Goods
        fields = ['name','goods_id']

'''商品信息 过滤
名称、介绍 模糊匹配

'''
class GoodsSearchFilter(filters.FilterSet):
    """
    商品的过滤类
    """
    name = filters.CharFilter(field_name='name', lookup_expr='contains', help_text='商品名模糊匹配')  # 包含关系，模糊匹配
    goods_brief = filters.CharFilter(field_name='goods_brief', lookup_expr='contains', help_text='分类名模糊匹配')  # 包含关系，模糊匹配
    # desc = filters.CharFilter(field_name='goods_desc', lookup_expr='contains', help_text='分类名模糊匹配')  # 包含关系，模糊匹配

    class Meta:
        model = Goods
        fields = ['name','goods_brief']
