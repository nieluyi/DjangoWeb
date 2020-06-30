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
import xadmin
from django.views.static import serve
from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static
from xiaohei.settings import MEDIA_ROOT, MEDIA_URL, STATIC_ROOT
from rest_framework.documentation import include_docs_urls



urlpatterns = [
    url('adminx/',xadmin.site.urls),
    url(r'^upload/(?P<path>.*)$', serve, {'document_root': MEDIA_ROOT}),
    url(r'^static/(?P<path>.*)$', serve, {'document_root': STATIC_ROOT}),
    url('^users/', include(('users.urls','users'), namespace='users')),
    # url('^ckeditor/', include(('ckeditor_uploader.urls','goods'),namespace='goods')),  # 配置富文本编辑器url
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    url('^goods/', include(('goods.urls', 'goods'), namespace='goods')),
    url('^trade/', include(('trade.urls', 'trade'), namespace='trade')),
    url('^pay/', include(('mypay.urls', 'mypay'), namespace='mypay')),
    url(r'docs/', include_docs_urls(title='接口文档'), name='docs'),    #django自带AutoSchema

]
# 上传的文件能直接通过url打开
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)