from rest_framework import serializers
from .models import Goods, GoodsCategory, GoodsImage, Banner, GoodsCategoryBrand
from django.db.models import Q

# 轮播图 +goods id、name
class BannerSerializer(serializers.ModelSerializer):
    # 正向关联
    goods_id = serializers.CharField(source='goods.goods_id')
    goods_name=serializers.CharField(source='goods.name')

    class Meta:
        model = Banner
        fields = "__all__"




class CategorySerializer3(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategory
        fields = '__all__'




class CategorySerializer2(serializers.ModelSerializer):
    sub_category = CategorySerializer3(many=True)  # 通过二级分类获取三级分类

    class Meta:
        model = GoodsCategory
        fields = '__all__'





class CategorySerializer(serializers.ModelSerializer):
    sub_category = CategorySerializer2(many=True)  # 通过一级分类获取到二级分类，由于一级分类下有多个二级分类，需要设置many=True

    class Meta:
        model = GoodsCategory
        fields = '__all__'


# 商品图片 序列化
class GoodsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsImage
        fields = ['image']  # 需要的字段只需要image

#商品详细信息 序列
class GoodsSerializer(serializers.ModelSerializer):
    category = CategorySerializer()  # 自定义字段覆盖原有的字段，实例化
    images = GoodsImageSerializer(many=True)  # 字段名和外键名称一样，商品轮播图，需要加many=True，因为一个商品有多个图片

    class Meta:
        model = Goods
        fields = '__all__'



'''2 商品列表 搜索

1 Goods 模型部分序列化 GoodsListSerializer
2 GoodsCategory 模型 反向序列化 AverseListSerializer
3 django的bug需要破环原有的序列数据，即加上一句错误代码，再更新，serializer才会自动更新
'''

# 商品详细信息 序列
class GoodsListSerializer(serializers.ModelSerializer):
    # images = GoodsImageSerializer()#更新序列化数据
    class Meta:
        model = Goods
        fields = ['goods_id', 'goods_sn', 'goods_num', 'name', 'market_price',
                  'shop_price', 'goods_brief', 'ship_free','is_hot','goods_front_image']

# 商品分类：反向商品列表
class AverseListSerializer(serializers.ModelSerializer):
    goods = GoodsListSerializer(read_only=True, many=True)  # 该实例 仍需 添加到下面的fields中
    class Meta:
        model = GoodsCategory
        fields = ['category_id','name','code','category_type','goods']

#---------------------------------------------------------------------------------------------------------


# 获取父级分类
class ParentCategorySerializer3(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategory
        fields = '__all__'


class ParentCategorySerializer2(serializers.ModelSerializer):
    parent_category = ParentCategorySerializer3()

    class Meta:
        model = GoodsCategory
        fields = '__all__'


class ParentCategorySerializer(serializers.ModelSerializer):
    parent_category = ParentCategorySerializer2()

    class Meta:
        model = GoodsCategory
        fields = '__all__'

# 品牌图片
class BrandsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategoryBrand
        fields = "__all__"


''' 1 商品分类

1 从 二级分类 中获取 商品信息 CategoryGoodsSerializer
2 整合 分类 和 商品 序列化 IndexCategoryGoodsSerializer
  逻辑：分类1-分类2-商品
'''


class CategoryGoodsSerializer(serializers.ModelSerializer):
    sub_category = CategorySerializer3(many=True)        # 通过二级分类获取三级分类

    goods = serializers.SerializerMethodField()          # 自定义序列化方法 get_goods 即该方法
    goods_filds = ['images', 'category', 'goods_desc']   #过滤的 goods 的字段
    def get_goods(self, obj):
        # 查询每级分类下的所有商品 # self 是 上面继承的类
        all_goods = Goods.objects.filter(Q(category_id=obj.category_id) | Q(category__parent_category_id=obj.category_id) | Q(category__parent_category__parent_category_id=obj.category_id))
        # 将查询的商品集进行序列化
        goods_serializer = GoodsSerializer(all_goods, many=True, context={'request': self.context['request']})
        # 返回json对象
        print(type(goods_serializer.data))
        # 过滤字段
        for i in goods_serializer.data:
            for j in self.goods_filds:
                i.pop(j)
        return goods_serializer.data

    class Meta:
        model = GoodsCategory
        fields = '__all__'


class IndexCategoryGoodsSerializer(serializers.ModelSerializer):
    # brands = BrandsSerializer(many=True)  # 分类下的品牌图片
    # goods = GoodsSerializer(many=True)  # 不能这样用，因为现在需要的是一级分类，而大多数商品是放在三级分类中的，所以很多商品是取不到的，所以到自己查询一级分类子类别下的所有商品
    sub_category = CategoryGoodsSerializer(many=True)  # 序列化二级分类

    ad_goods = serializers.SerializerMethodField()  # 广告商品可能加了很多，取每个分类第一个
    def get_ad_goods(self, obj):
        all_ads = obj.ads.all()
        if all_ads:
            ad = all_ads.first().goods  # 获取到商品分类对应的商品
            ad_serializer = GoodsSerializer(ad, context={'request': self.context['request']})  # 序列化该广告商品，嵌套的序列化类中添加context参数，可在序列化时添加域名
            return ad_serializer.data
        else:
            # 在该分类没有广告商品时，必须要返回空字典，否则Vue中取obj.id会报错
            return {}

    class Meta:
        # 继承与 GoodsCategory 无关的  goods
        model = GoodsCategory
        fields = '__all__'
