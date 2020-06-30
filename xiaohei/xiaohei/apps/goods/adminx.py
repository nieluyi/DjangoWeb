#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2018/7/1 00:49
# @User    : zhunishengrikuaile
# @File    : adminx.py
# @Email   : NAME@SHUJIAN.ORG
# @MyBlog  : WWW.SHUJIAN.ORG
# @NetName : 書劍
# @Software: 一起哟预约报名小程序后端
import xadmin

from goods.models import GoodsCategory,GoodsCategoryBrand,Goods, GoodsImage,Banner,IndexCategoryAd

#首页轮播图管理
class BannerModelAdmin(object):
    list_display = ['goods' ,'image', 'index', 'add_time']  # 列表页显示
    model_icon = "fa fa-bookmark"  # 这样可以替换与设置原有的Xadmin的图标
    list_editable = ('is_tab',)  # 列表页可编辑

#商品分类管理
class GoodsCategoryModelAdmin(object):
    list_display = ['name', 'category_type', 'image','is_tab', 'parent_category']  # 列表页显示

    list_editable = ('is_tab',)     # 列表页可编辑

#商品详情管理
class GoodsImageInline(object):
    model = GoodsImage
class GoodsModelAdmin(object):
    list_display = ['name','goods_id']
    inlines = [
        GoodsImageInline
    ]


#
class IndexCategoryAdModelAdmin(object):
    list_display = ['category', 'goods']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            # 外键下拉框添加过滤
            kwargs['queryset'] = GoodsCategory.objects.filter(category_type=1)
        return super(IndexCategoryAdModelAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


# all_models = apps.get_app_config('goods').get_models()
# for model in all_models:
#     try:
#         admin.site.register(model)
#     except:
#         pass
xadmin.site.register(Banner,BannerModelAdmin)#商品详情
xadmin.site.register(GoodsCategory,GoodsCategoryModelAdmin)#商品分类
xadmin.site.register(Goods,GoodsModelAdmin)#商品详情
xadmin.site.register(IndexCategoryAd,IndexCategoryAdModelAdmin)

