#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2018/7/10 22:12
# @User    : zhunishengrikuaile
# @File    : adminx.py
# @Email   : NAME@SHUJIAN.ORG
# @MyBlog  : WWW.SHUJIAN.ORG
# @NetName : 書劍
# @Software: 一起哟预约报名小程序后端

import xadmin

from trade.models import OrderInfo,OrderGoods,ShoppingCart
#购物车信息
class ShoppingCartViewAdmin(object):
    '''
    用户表显示
    '''
    list_display = ['user']  # 后台显示类型
    search_fields = ['user']  # 设置搜索
    list_filter = ['user']  # 搜索过滤器
    model_icon = "fa fa-list-alt"

#订单信息
class OrderInfoViewAdmin(object):
    '''
    用户表显示
    '''
    list_display = ['user']  # 后台显示类型
    search_fields = ['user']  # 设置搜索
    list_filter = ['user']  # 搜索过滤器

#订单商品详情
class OrderGoodsViewAdmin(object):
    '''
    用户表显示
    '''
    list_display = ['order']  # 后台显示类型
    search_fields = ['order']  # 设置搜索
    list_filter = ['order']  # 搜索过滤器


# xadmin.site.unregister(UserProFile)
xadmin.site.register(OrderInfo, OrderInfoViewAdmin)  # 普通用户
xadmin.site.register(ShoppingCart, ShoppingCartViewAdmin)  # 普通用户
xadmin.site.register(OrderGoods,OrderGoodsViewAdmin)  # 普通用户
