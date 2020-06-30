from rest_framework import serializers
from goods.models import Goods
from trade.models import ShoppingCart, OrderInfo, OrderGoods
from goods.serializers import GoodsSerializer,GoodsListSerializer
# from utils.alipay import AliPay, get_server_ip
# from DjangoOnlineFreshSupermarket.settings import app_id, alipay_debug, alipay_public_key_path, app_private_key_path


class ShoppingCartListSerializer(serializers.ModelSerializer):
    goods = GoodsListSerializer(many=False)  # 一个购物车的记录只会对应一个商品，默认many=False，也就是可以不写

    class Meta:
        model = ShoppingCart
        fields = "__all__"



class ShoppingCartSerializer(serializers.Serializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()  # 表示user为隐藏字段，默认为获取当前登录用户
    )
    nums = serializers.IntegerField(required=True,label='商品数量', help_text='商品数量',
                                    error_messages={
                                        'min_value': '商品数量不能小于1',
                                        'required': '请选择购买数量'
                                    })
    goods = serializers.PrimaryKeyRelatedField(queryset=Goods.objects.all(),many=True, required=True, label='商品')


    # goodsList = serializers.ListField(required=True,label='商品id', help_text='商品id')

    # 在序列化中使用create，参数self.context['request']相当于 views中的request
    # validated_data 是 经过验证的序列化数据 ；包含attrs数据（get、post传送的数据）
    #         validated_data = dict(
    #             list(self.validated_data.items()) +
    #             list(kwargs.items())
    # kwargs 是get、post传递的数据；那么**validated_data则是二者结合的模型类数据
    # 传入参数 nums  goods（模型包含字段）
    def validate(self, attrs):
        print('查看数据',attrs)
        return attrs
    def create(self, validated_data):
        # instance = super(ShoppingCartSerializer, self).create(validated_data)
        # print(validated_data)
        user = self.context['request'].user  # serializer中获取当前用户，而views是直接从request中获取
        nums = validated_data['nums']
        goods = validated_data['goods']
        # print('查看拿数据',goods)
        # print('查看数据类型',type(goods[0]))
        for good in goods:
        # 查询记录是否存在，存在，则进行数量加，不存在则新创建
            shopping_cart = ShoppingCart.objects.filter(user=user, goods=good)  #这句比较巧妙，筛选条件是两个 1 是用户 2 是商品 ；即用户下的商品是唯一的
            if shopping_cart:
                shopping_cart = shopping_cart.first()
                shopping_cart.nums += nums    #可以通过这里设置购物车增减，这种要求操作快捷的，最好前端组织数据，后端负责更新，
                shopping_cart.save()
                # 删除 购物车 商品
                # if shopping_cart.nums <=0:
                #     shopping_cart.delete()
            else:
                shopping_cart = ShoppingCart.objects.create(**validated_data)    #validated_data返回模型类对象
            # 最后要返回创建后的结果；返回 用户购物车
            yield shopping_cart
    # instance 是 creat 里面创建的模型类对象
    def update(self, instance, validated_data):
        instance.nums = validated_data['nums']  # 从validated_data中获取商品数量去更新购物车
        instance.save()
        return instance


class OrderInfoSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()  # 表示user为隐藏字段，默认为获取当前登录用户
    )
    order_sn = serializers.CharField(read_only=True)  # 只能读，不能显示给用户修改，只能后台去修改
    trade_no = serializers.CharField(read_only=True)  # 只读
    pay_status = serializers.CharField(read_only=True)  # 只读
    pay_time = serializers.DateTimeField(read_only=True)  # 只读
    # alipay_url = serializers.SerializerMethodField()  # 生成支付宝url

    def generate_order_sn(self):
        # 当前时间+userid+随机数
        import time
        from random import randint
        order_sn = '{time_str}{user_id}{random_str}'.format(time_str=time.strftime('%Y%m%d%H%M%S'), user_id=self.context['request'].user.id, random_str=randint(10, 99))
        return order_sn

    def validate(self, attrs):
        # 数据验证成功后，生成一个订单号
        attrs['order_sn'] = self.generate_order_sn()
        return attrs

    # def get_alipay_url(self, obj):
    #     # 方法命名规则为：get_<field_name>
    #     server_ip = get_server_ip()
    #     alipay = AliPay(
    #         app_id=app_id,  # 自己支付宝沙箱 APP ID
    #         notify_url="http://{}:8000/alipay/return/".format(server_ip),
    #         app_private_key_path=app_private_key_path,  # 可以使用相对路径那个
    #         alipay_public_key_path=alipay_public_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
    #         debug=alipay_debug,  # 默认False,
    #         return_url="http://{}:8000/alipay/return/".format(server_ip)
    #     )
    #     # 创建订单
    #     order_sn = obj.order_sn
    #     order_amount = obj.order_amount
    #     url = alipay.direct_pay(
    #         subject="生鲜超市-{}".format(order_sn),
    #         out_trade_no=order_sn,
    #         total_amount=order_amount,
    #         # return_url="http://{}:8000/alipay/return/".format(server_ip)  # 支付完成后自动跳回该url，可以不填了，因为初始化已经加上了
    #     )
    #     re_url = "https://openapi.alipaydev.com/gateway.do?{data}".format(data=url)
    #     return re_url

    class Meta:
        model = OrderInfo
        fields = "__all__"


# 订单中的商品序列化
class OrderGoodsSerializer(serializers.ModelSerializer):
    goods = GoodsSerializer()  # 直接用goods.serializers商品详情的序列化

    class Meta:
        model = OrderGoods
        fields = "__all__"


# 订单详情序列化
class OrderInfoDetailSerializer(serializers.ModelSerializer):
    order_goods = OrderGoodsSerializer(many=True)  # 为OrderGoods中外键关联名称
    # alipay_url = serializers.SerializerMethodField()  # 生成支付宝url
    #返回支付宝订单url
    # def get_alipay_url(self, obj):
    #     # 方法命名规则为：get_<field_name>
    #     server_ip = get_server_ip()
    #     alipay = AliPay(
    #         app_id=app_id,  # 自己支付宝沙箱 APP ID
    #         notify_url="http://{}:8000/alipay/return/".format(server_ip),
    #         app_private_key_path=app_private_key_path,  # 可以使用相对路径那个
    #         alipay_public_key_path=alipay_public_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
    #         debug=alipay_debug,  # 默认False,
    #         return_url="http://{}:8000/alipay/return/".format(server_ip)
    #     )
    #     # 创建订单
    #     order_sn = obj.order_sn
    #     order_amount = obj.order_amount
    #     url = alipay.direct_pay(
    #         subject="生鲜超市-{}".format(order_sn),
    #         out_trade_no=order_sn,
    #         total_amount=order_amount,
    #         # return_url="http://{}:8000/alipay/return/".format(server_ip)  # 支付完成后自动跳回该url，可以不填了，因为初始化已经加上了
    #     )
    #     re_url = "https://openapi.alipaydev.com/gateway.do?{data}".format(data=url)
    #     return re_url

    class Meta:
        model = OrderInfo
        fields = "__all__"
