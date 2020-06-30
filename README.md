# DjangoWeb
django建立微信商城小程序的后端管理系统  
简单介绍一下项目：  
  主要是在学习黑马优购商城前端时因为后台接口不能满足自己设计的需要特此建立的后端系统。  
  包含四个版块 商品信息：goods  
             微信支付：mypay  
             订单信息：trade  
             用户信息：users  
如果想使用该项目，首先cd 至项目目录输入，  
  pip --default-timeout=100 install -r reuirements.txt -i https://pypi.douban.com/simple/  
安装完毕后  
  
mysql数据库  
创建dssx2的databse；也可以配置xiaohei/settings.py下面的 DATABASES  
  
数据库生成数据表  
   生成迁移文件：python manage.py makemigrations  
   迁移：python manage.py migrate  

创建管理员：python manage.py createsuperuser  
输入  
username:   ****  
email  :   ****  
password:   ****  
启动服务器  
python manage.py runserver  

因为是结合微信小程序的后端，在用户信息创建和验证均需要用到微信接口，所以需要申请一个小程序的appid，申请到后在 xiaohei/sys_info.py 文件填写  
   MINI_APP_ID = ''  
   MINI_APP_SECRET = ''  
这里记住如果你是测试号开发的微信小程序，请在微信开发者工具中也要修改appid，不然请求会报错  
  
微信小程序支付接口需要绑定商户号，还需要微信认证300块大洋，我这里心疼钱，支付这里没有接着往下写，也就是trade、mypay里面的订单回调的逻辑没有写完全  
如果哪位感兴趣可以完善下  
  
项目成功运行后输入  
http://127.0.0.1:8000/docs/  
该地址是接口文档，开发小程序的朋友通过这个文档进行接口的调试  
