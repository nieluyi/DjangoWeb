# -*- coding: utf-8 -*-
import os
import sys
import requests
import datetime
from PIL import Image
from io import BytesIO
from rest_framework import status
from rest_framework import mixins
from django.shortcuts import render
from rest_framework import authentication
from rest_framework import views, viewsets
from rest_framework.response import Response
from utils.weixin_util.weixin import WXAPPAPI
from utils.permissions import IsOwnerOrReadOnly  # 登陆验证
from rest_framework.mixins import CreateModelMixin
from django.contrib.auth.backends import ModelBackend
from rest_framework.permissions import IsAuthenticated  # 登陆验证
from rest_framework_jwt.views import JSONWebTokenAPIView  # 重写jwt的认证
from utils.weixin_util.weixin.lib.wxcrypt import WXBizDataCrypt
from django.contrib.auth.hashers import make_password, check_password
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.serializers import (
    JSONWebTokenSerializer
)
from rest_framework_jwt.settings import api_settings
from xiaohei.sys_info import MINI_APP_ID, MINI_APP_SECRET
from users.models import UserProFile
from xiaohei.settings import BASE_DIR
from xiaohei.settings import IMAGES_URL
from users.Serializers import UserRegSerializer
from django.contrib.auth import get_user_model
from django.db.models import Q
jwt_response_payload_handler = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER

''' 
1 注册 
    用户信息 存储 与 返回
    1 存储： post请求接收、校验 用户id 、
         存在用户 则 返回已存在的 token、注册成功为空
         不存在   则 创建并保存  返回生成的token、注册成功标签
    class  Registered
2 登录
  wx.login() 获取 临时登录凭证code ，并回传到开发者服务器
  微信自带加密 若要在网页 临时登录 并获取信息 需要 调用 code2Session 接口，换取 用户唯一标识 OpenID 和 会话密钥 session_key。
        code：服务器用来获取sessionKey的必要参数。
        IV：加密算法的初始向量，
        encryptedData：加密过的字符串。
       （ 接口获取 seesionKey，然后在通过 sessionKey 和 iv 来解密encryptedData数据获取UnionID ）
    1 post 请求 附带用户id 密码
    2 校验 数据库中的 用户id == post.用户id  用户密码 == post.用户密码
           若不存在 判断 有无用户名
'''

User = get_user_model()

#自定义验证规则
class CustomBackend(ModelBackend):
    '''
    '''

    def authenticate(self, request, username=None, password=None, **kwargs):
        '''
        :param request:
        :param username:
        :param password:
        :param kwargs:
        :return:
        '''
        try:
            user = User.objects.get(Q(username=username) | Q(mobile=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None

''' 1 使用微信 注册本地的用户信息
      包含两个类   Registered
                 
'''
class Registered(CreateModelMixin, mixins.UpdateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    '''
    Registered
    '''

    serializer_class = UserRegSerializer
    queryset = UserProFile.objects.all()

    authentication_classes = (authentication.SessionAuthentication, JSONWebTokenAuthentication)  # 认证

    def get_permissions(self):
        '''
        :return:
        '''
        if self.action == "retrieve":
            return [IsAuthenticated()]#permissions.IsAuthenticated()
        elif self.action == "create":
            return []
        return []
        pass

    def create(self, request, *args, **kwargs):

        # try:
        #调用微信api接口获取用户登录信息，
        api = WXAPPAPI(appid=MINI_APP_ID, app_secret=MINI_APP_SECRET)
        code = request.data['code']  # 获取到code
        session_info = api.exchange_code_for_session_key(code=code) # authorize_url, url_params
        session_key = session_info.get('session_key') # response.content.decode()
        crypt = WXBizDataCrypt(MINI_APP_ID, session_key) #

        encrypted_data = request.data['username']  # 获取到encrypted_data
        iv = request.data['password']  # 获取到iv
        user_info = crypt.decrypt(encrypted_data, iv)  # 获取到用户的登陆信息
        # 获取用户的信息
        openid = user_info['openId']  # 获取openid
        avatarUrl = user_info['avatarUrl']  # 获取头像
        country = user_info['country']  # 获取国家
        province = user_info['province']  # 获取城市
        city = user_info['city']  # 获取区域
        gender = user_info['gender']  # 获取性别
        language = user_info['language']  # 获取语言
        nickName = user_info['nickName']  # 获取昵称
        # 保存用户头像到本地
        avatarPath = os.path.join(BASE_DIR, 'upload/UserProFilebg/avatar/')
        avatarGet = requests.get(avatarUrl)
        avatar_name = avatarPath + openid + '.png'
        image = Image.open(BytesIO(avatarGet.content))
        image.save(avatar_name)
        # 判断用户是否存在
        if UserProFile.objects.filter(openid=openid):
            this_user = UserProFile.objects.filter(openid=openid)
            this_user.nickName = nickName  # 更新用户的微信昵称
            this_user.avatarUrl = avatarUrl  # 更新用户微信头像
            this_user.gender = str(gender)  # 更新用户的性别
            this_user.avatar = 'avatar/' + openid + '.png'
            this_user.update()
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            # 保存用户信息
            if len(nickName) > 6:
                nickName = nickName[0:6]
            user_info_save = UserProFile()
            user_info_save.openid = openid  # 保存用户openid
            user_info_save.avatarUrl = avatarUrl  # 保存用户微信头像
            user_info_save.country = country  # 保存用户所在的国家
            user_info_save.province = province  # 保存用户所在的城市
            user_info_save.city = city  # 保存用户所在的区域
            user_info_save.avatar = 'UserProFilebg/avatar/' + openid + '.png'
            user_info_save.gender = str(gender)  # 保存用户的性别
            user_info_save.language = language  # 保存用户当前使用的语言
            user_info_save.nickName = nickName  # 保存用户的微信昵称
            user_info_save.name = nickName  # 用户原始的用户名
            user_info_save.username = openid  # 保存用户的昵称
            user_info_save.password = make_password(openid)  # 保存用户的密码
            user_info_save.zhong_jifen = 0
            user_info_save.save()
        # except:
        #     return Response(status=status.HTTP_401_UNAUTHORIZED)


        return Response(status=status.HTTP_201_CREATED)

    def get_object(self):
        '''
        :return:
        '''
        return self.request.user

    def perform_create(self, serializer):
        '''
        :param serializer:
        :return:
        '''
        return serializer.save()

'''  2 修改和获取用户的个人信息
1 对 token 进行认证
2 获取 request 中的信息更改 数据库
    def get  显示 数据库中的字段信息
    def post 
'''
class GetUser(views.APIView):
    '''
    修改和获取用户的个人信息
    这里因为是已经登录的 直接用token验证是否是本地的用户 就可以从其中获取数据  并返回数据
    '''
    authentication_classes = (authentication.SessionAuthentication, JSONWebTokenAuthentication)  # Token验证
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    def get(self, request):
        '''
        获取用户信息
        :param request:
        :return:
        '''
        # 从 request 获取 用户信息
        name = self.request.user.name
        avatar = self.request.user.avatar
        thesignature = self.request.user.thesignature
        background = self.request.user.background
        gender = self.request.user.gender
        birthay = self.request.user.birthay
        nickName = self.request.user.nickName
        mobile = self.request.user.mobile
        if gender == '1':
            gender = '男'
        else:
            gender = '女'
        user_info = {
            'name': name,
            'avatar': IMAGES_URL + 'upload/' + str(avatar),
            'thesignature': thesignature,
            'gender': gender,
            'nickName': nickName,
            'mobile': mobile,
            'birthay': datetime.datetime.strftime(birthay, "%Y-%m-%d"),
            'background': IMAGES_URL + 'upload/' + str(background)
        }
        return Response(user_info, status=status.HTTP_200_OK)
    # 接收
    # 接收本地修改数据的 post 请求
    # 接收参数  'types'：'修改字段类型'  'file':'修改内容'
    def post(self, request, format=None):
        '''
        修改用户个人信息
        :param request:
        :return:
        '''
        try:
            type = request.data['types']
        except:
            type = None
        # if (type != None) and (image_files != None):
        if type == 'GHTX':
            image_files = request.data['file']
            self.request.user.avatar = image_files
            self.request.user.save()
            return Response(status=status.HTTP_200_OK)
        elif type == 'GHBJ':
            image_files = request.data['file']
            self.request.user.background = image_files
            self.request.user.save()
            return Response(status=status.HTTP_200_OK)
        elif type == 'GHXB':
            self.request.user.gender = request.data['new_shengri']
            self.request.user.save()
            return Response(status=status.HTTP_200_OK)
        elif type == 'GHSRI':
            self.request.user.birthay = request.data['sr']
            self.request.user.save()
            return Response(status=status.HTTP_200_OK)
        elif type == 'GHNAME':
            name_all = UserProFile.objects.filter(name=request.data['new_name'])
            if name_all:
                return Response({'message': '昵称已存在'}, status=status.HTTP_202_ACCEPTED)
            self.request.user.name = request.data['new_name']
            self.request.user.save()
            return Response({'message': '昵称更改成功'}, status=status.HTTP_200_OK)
        elif type == 'GHPHONE':
            phone_all = UserProFile.objects.filter(mobile=request.data['new_phone'])
            if phone_all:
                return Response({'message': '手机号已存在'}, status=status.HTTP_202_ACCEPTED)
            self.request.user.mobile = request.data['new_phone']
            self.request.user.save()
            return Response({'message': '手机号已更换'}, status=status.HTTP_200_OK)
        elif type == 'thesignature':
            self.request.user.thesignature = request.data['new_thesignature']
            self.request.user.save()
            return Response({'message': '签名已更新'}, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_401_UNAUTHORIZED)



'''3 登录
get_serializer_context
1 微信 api 解析获得 openid和session_key
2  crypt.decrypt(encrypted_data, iv) 解密 useinfo 信息
3  this_user = UserProFile.objects.filter(openid=openid) 检索数据库中 用户唯一id
4  更新用户信息 昵称和头像
5  删除临时登录凭证 code
7  返回自身 

6  签发jwt登录凭证token


'''
class READJSONWebTokenAPIView(JSONWebTokenAPIView):
    """
    API View that receives a POST with a user's username and password.

    Returns a JSON Web Token that can be used for authenticated requests.
    """


    '''
    get_serializer_context 返回的类 由 get_serializer 继承 给 kwargs['context']  **kwargs 为传参的容器
    '''

    # get_serializer_context  与 post 函数的联系
    def post(self, request, *args, **kwargs):
        #################################################################
        # 这段为 编辑 验证字段的逻辑 主要是讲 request的'username' 'password' 都设置为用户唯一id openId
        # 这里 缺一段 类之间 self的传递 搞不清楚
        try:
            username = request.data.copy()
            print(1)
            api = WXAPPAPI(appid=MINI_APP_ID, app_secret=MINI_APP_SECRET)
            print(2)
            code = username['code']  # 获取到code
            session_info = api.exchange_code_for_session_key(code=code)
            session_key = session_info.get('session_key')
            crypt = WXBizDataCrypt(MINI_APP_ID, session_key)
            print(3)
            encrypted_data = username['username']  # 获取到encrypted_data
            iv = username['password']  # 获取到iv
            user_info = crypt.decrypt(encrypted_data, iv)  # 获取到用户的登陆信息
            print(4)
            # 获取用户的信息
            openid = user_info['openId']  # 获取openid
            avatarUrl = user_info['avatarUrl']  # 获取到头像
            nickName = user_info['nickName']  # 获取昵称
            # 找到用户更新用户的微信昵称和头像
            this_user = UserProFile.objects.filter(openid=openid)
            print(5)
            if this_user:
                this_user = this_user[0]
                this_user.avatarUrl = avatarUrl
                this_user.nickName = nickName
                # this_user.avatar = 'avatar/' + openid + '.png'
                this_user.save()
            print(6)
            username['username'] = openid
            username['password'] = openid
            del username['code']
        except:
            print('失败')
            pass
        ##################################################################
        serializer = self.get_serializer(data=username)


        if serializer.is_valid():
            user = serializer.object.get('user') or request.user
            token = serializer.object.get('token')
            response_data = jwt_response_payload_handler(token, user, request)
            print(response_data)
            response = Response(response_data)

            # token = Token.objects.create(user=...)
            # print(token.key)

            if api_settings.JWT_AUTH_COOKIE:
                expiration = (datetime.utcnow() +
                              api_settings.JWT_EXPIRATION_DELTA)
                response.set_cookie(api_settings.JWT_AUTH_COOKIE,
                                    token,
                                    expires=expiration,
                                    httponly=True)
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#向obtain_jwt_token发送post请求，即调用其父类 JSONWebTokenAPIView 的post方法，
#不懂的话可参考[如何根据请求方法调用相应函数](https://blog.csdn.net/hyh294673057/article/details/97616369)

# rest_framework_jwt自带的jwt生成            、验证和刷新的方式
class ObtainJSONWebToken(READJSONWebTokenAPIView):
    """
    API View that receives a POST with a user's username and password.

    Returns a JSON Web Token that can be used for authenticated requests.
    """
    serializer_class = JSONWebTokenSerializer




