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
from xadmin import views  # 引入xadmin的主题视图来支持主题选择
from users.models import UserProFile


class GlobalSetting(object):
    site_title = "药品商城后台"
    site_footer = "药品商城后台"
    menu_style = "accordion"  # 把App收缩起来

class UserProFileAdmin(object):
    '''
    用户表显示
    '''
    list_display = ["name", "nickName", "mobile", "gender", 'language', 'country',
                    'province',
                    'city']  # 后台显示类型
    search_fields = ["name", "nickName", "mobile", "gender", 'language', 'country', 'province',
                     'city']  # 设置搜索
    list_filter = ["name", "nickName", "mobile", "gender", 'language', 'country', 'province',
                   'city']  # 搜索过滤器
    model_icon = "fa fa-tags"

xadmin.site.unregister(UserProFile)
xadmin.site.register(UserProFile, UserProFileAdmin)  # 普通用户
xadmin.site.register(views.CommAdminView, GlobalSetting)  # 注册修改xadmin后台的页头和底部信息