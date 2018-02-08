from django.shortcuts import render

# Create your views here.
from django.shortcuts import HttpResponse
from api.auth_code import create_validate_code
from io import BytesIO
from base64 import b64encode
from api.host_manage import Host_API
import hashlib,time,json,random,string
from host_manage.models import UserInfo

def index(request):
    try:
        access_token = request.META['HTTP_ACCESSTOKEN']
    except KeyError:
        access_token = request.COOKIES.get("accessToken",None)
    # del request.session["user"]
    print(access_token)
    user = request.session.get("user",None)
    if user == None:
        msg = "用户登录"
        url = "/login/"
        lg_out = ""
    else:
        user_info = UserInfo.objects.filter(user=user)
        msg = "欢迎，" + user_info[0].name
        url = ""
        lg_out = "退出登录"
    print(user)
    return render(request,"host_manage/index.html",{"msg":msg,"url":url,"lg_out":lg_out})



def login_out(request):
    request.session.clear()
    msg = "用户登录"
    url = "/login/"
    lg_out = ""
    return render(request, "host_manage/index.html", {"msg": msg, "url": url,"lg_out":lg_out})


def host(request):
    pass



def setting(request):
    pass



def api(request):
    if request.method == 'POST':
        act = request.POST.get("act",None)
    else:
        act = request.GET.get("act", None)
    if act == 'check_user':
        res = Host_API(request).check_user()
    elif act == 'register':
        res = Host_API(request).register()
    elif act == 'check_sign':
        res = Host_API(request).check_sign()
    else:
        res = {
            "errNum": 301,
            "errMsg": "错误参数",
            "data": False,
        }

    return HttpResponse(json.dumps(res),content_type="application/json")
















def login(request):
    if request.method == 'POST':
        # print(request.META['HTTP_ACCESSTOKEN'])
        # print(request.POST)
        user = request.POST.get("user",None)
        pwd = request.POST.get("pwd",None)
        check_code = request.POST.get("auth_code",None)
        check_code = check_code.lower()
        server_check_code = request.session['check_code']
        server_check_code = server_check_code.lower()
        res = {}
        Hres = HttpResponse()
        if check_code == server_check_code:
            user_info = UserInfo.objects.filter(user=user)
            if user_info[0].user == user and user_info[0].pwd == pwd:
                # 颁发签证
                nonce = ''.join(random.sample(string.ascii_letters + string.digits, 16))
                key = user_info[0].key
                t = int(time.time())
                sign_array = [str(t), nonce, key]
                sign_str = "".join(sorted(sign_array))
                server_signature = hashlib.sha1(sign_str.encode()).hexdigest()
                # 保存签名并设置过期时间
                request.session['sign'] = server_signature
                request.session['sign_timeout'] = time.time()+3600*24 # 默认过期时间一天
                res = {
                    "errNum":0,
                    "errMsg":"ok",
                    "access_token":server_signature,
                }
                request.session['user'] = user
                Hres.set_cookie(key="accessToken", value=server_signature, expires=time.time() + 36000)
            else:
                res = {
                    "errNum": 100,
                    "errMsg": "用户名或密码错误",
                }
        else:
            res = {
                "errNum": 101,
                "errMsg": "验证码错误",
            }
        time.sleep(1)
        Hres.content = json.dumps(res)
        Hres.content_type = 'application/json'
        return Hres
    else:
        auth_code(request)
    return render(request,'host_manage/login.html')


def auth_code(request):
    f = BytesIO()
    img, code = create_validate_code()
    request.session['check_code'] = code
    img.save(f, 'PNG')
    img_data = b64encode(f.getvalue())
    return HttpResponse(img_data)