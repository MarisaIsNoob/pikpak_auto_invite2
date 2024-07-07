from flask import Flask, request, Response, render_template
from multiprocessing import Pool
from functools import partial
from tqdm import trange
import numpy as np
import requests
import hashlib
import random
import json
import uuid
import time
import cv2
import re

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/run-script', methods=['POST'])
def run_script():
    invite_code = request.json.get('invite_code')
    print('现在是6.0版本好吧!!!')
    print('强烈建议replit运行!!!')
    print('成功与否全凭运气, 成功率较高, 请自行测试, 祝使用愉快!')
    # 有三个邮箱接口,EMAIL_CHOOSE默认为1,自行测试!!!
    print('最后，战斗!  爽!!!!')
    # EMAIL_CHOOSE变量为1或者2为临时邮箱，无需配置
    # EMAIL_CHOOSE变量为3或者4为配置邮箱，需要自己配置。邮箱采用转发临时邮箱，切勿多人同时使用，否则验证码可能混乱!!!
    EMAIL_CHOOSE = 1

    # 获取用户输入的邀请码

    # 假设这里是你的 Python 代码执行部分，输出到前端
    def generate_output():
        yield '开始运行...\n'
        # 调用main函数，传入邀请码和EMAIL_CHOOSE变量
        try:
            change_ip = get_change_ip()
            start_time = time.time()
            print(f'程序开始运行,ip选取为:{change_ip}')
            # 生成唯一标识符
            xid = str(uuid.uuid4()).replace('-', '')
            # 选择邮箱
            email = choose_email(EMAIL_CHOOSE)
            yield '获取邮箱信息:' + email + '\n'
            # 初始化
            Init = init(xid, email, change_ip)
            yield '初始安全验证:\n' + str(Init) + '\n'
            # 无限循环，直到验证通过
            while True:
                # 获取图片信息
                yield '验证滑块...\n'
                img_info = get_image(xid, change_ip)
                # 判断是否验证通过
                if img_info['response_data']['result'] == 'accept':
                    print('验证通过!!!')
                    yield '验证通过!!!\n'
                    break
            # 获取新token
            captcha_token_info = get_new_token(img_info, xid, Init['captcha_token'], change_ip)
            yield '获取滑块验证token:\n' + str(captcha_token_info) + '\n'
            # 验证
            email_start_time = int(time.mktime(time.localtime()))
            Verification = verification(captcha_token_info['captcha_token'], xid, email, change_ip)
            yield '发送验证码...\n'
            # 获取邮箱验证码
            code = get_emailcode(EMAIL_CHOOSE, email, email_start_time)
            yield '获取到验证码:' + code + '\n'
            # 验证
            verification_response = verify(xid, Verification['verification_id'], code, change_ip)
            yield '验证验证码:\n' + str(verification_response) + '\n'
            # 注册
            signup_response = signup(xid, email, code, verification_response['verification_token'], change_ip)
            yield '注册结果:\n' + str(signup_response) + '\n'
            # 当前时间
            current_time = str(int(time.time()))
            # 获取签名
            sign = get_sign(xid, current_time)
            # 初始化1
            init1_response = init1(xid, signup_response['access_token'], signup_response['sub'], sign, current_time,
                                   change_ip)
            yield '二次安全验证:\n' + str(init1_response) + '\n'
            # 邀请
            Invite = invite(signup_response['access_token'], init1_response['captcha_token'], xid, change_ip)
            yield '确认邀请:\n' + str(Invite) + '\n'
            # 初始化2
            init2_response = init2(xid, signup_response['access_token'], signup_response['sub'], sign, current_time,
                                   change_ip)
            yield '三次安全验证:\n' + str(init2_response) + '\n'
            # 激活
            activation = activation_code(signup_response['access_token'], init2_response['captcha_token'], xid,
                                         invite_code, change_ip)
            yield '填写邀请:\n' + str(activation) + '\n'
            # 结束计时
            end_time = time.time()
            run_time = f'{(end_time - start_time):.2f}'
            try:
                if activation['add_days'] == 5:
                    print(f'邀请码: {invite_code} => 邀请成功, 运行时间: {run_time}秒')
                    print(f'邀请邮箱: {email}\n邮箱密码: pw123456')
                    yield '最后结果:\n' + f'邀请码: {invite_code} ==> 邀请成功\n' + f'运行时间: {run_time}秒\n' 
                    yield f'邀请邮箱: {email}\n邮箱密码: pw123456\n'
                elif activation['add_days'] == 0:
                    print(f'邀请码: {invite_code} ==> 邀请失败, 运行时间: {run_time}秒')
                    yield '最后结果:\n' + f'邀请码: {invite_code} ==> 邀请失败\n' + f'运行时间: {run_time}秒\n'
                else:
                    print(f'程序异常请重试!!!, 运行时间: {run_time}秒')
            except:
                print('检查你的邀请码是否有效!!!')

        # 捕获异常
        except Exception as e:
            print('异常捕获:', e)
            yield '异常捕获:\n' + str(e)
        yield '运行结束!!!'
    return Response(generate_output(), content_type='text/plain')


# =============================================函数===========================================
# 滑块数据加密
def r(e, t):
    n = t - 1
    if n < 0:
        n = 0
    r = e[n]
    u = r["row"] // 2 + 1
    c = r["column"] // 2 + 1
    f = r["matrix"][u][c]
    l = t + 1
    if l >= len(e):
        l = t
    d = e[l]
    p = l % d["row"]
    h = l % d["column"]
    g = d["matrix"][p][h]
    y = e[t]
    m = 3 % y["row"]
    v = 7 % y["column"]
    w = y["matrix"][m][v]
    b = i(f) + o(w)
    x = i(w) - o(f)
    return [s(a(i(f), o(f))), s(a(i(g), o(g))), s(a(i(w), o(w))), s(a(b, x))]


def i(e):
    return int(e.split(",")[0])


def o(e):
    return int(e.split(",")[1])


def a(e, t):
    return str(e) + "^⁣^" + str(t)


def s(e):
    t = 0
    n = len(e)
    for r in range(n):
        t = u(31 * t + ord(e[r]))
    return t


def u(e):
    t = -2147483648
    n = 2147483647
    if e > n:
        return t + (e - n) % (n - t + 1) - 1
    if e < t:
        return n - (t - e) % (n - t + 1) + 1
    return e


def c(e, t):
    return s(e + "⁣" + str(t))


def img_jj(e, t, n):
    return {"ca": r(e, t), "f": c(n, t)}


def md5(input_string):
    return hashlib.md5(input_string.encode()).hexdigest()


def get_sign(xid, t):
    e = [
        {"alg": "md5", "salt": "KHBJ07an7ROXDoK7Db"},
        {"alg": "md5", "salt": "G6n399rSWkl7WcQmw5rpQInurc1DkLmLJqE"},
        {"alg": "md5", "salt": "JZD1A3M4x+jBFN62hkr7VDhkkZxb9g3rWqRZqFAAb"},
        {"alg": "md5", "salt": "fQnw/AmSlbbI91Ik15gpddGgyU7U"},
        {"alg": "md5", "salt": "/Dv9JdPYSj3sHiWjouR95NTQff"},
        {"alg": "md5", "salt": "yGx2zuTjbWENZqecNI+edrQgqmZKP"},
        {"alg": "md5", "salt": "ljrbSzdHLwbqcRn"},
        {"alg": "md5", "salt": "lSHAsqCkGDGxQqqwrVu"},
        {"alg": "md5", "salt": "TsWXI81fD1"},
        {"alg": "md5", "salt": "vk7hBjawK/rOSrSWajtbMk95nfgf3"}
    ]
    md5_hash = f"YvtoWO6GNHiuCl7xundefinedmypikpak.com{xid}{t}"
    for item in e:
        md5_hash += item["salt"]
        md5_hash = md5(md5_hash)
    return md5_hash


# 网络请求函数
def init(xid, mail, change_ip):
    url = 'https://user.mypikpak.com/v1/shield/captcha/init'
    body = {
        "client_id": "YvtoWO6GNHiuCl7x",
        "action": "POST:/v1/auth/verification",
        "device_id": xid,
        "captcha_token": "",
        "meta": {
            "email": mail
        }
    }
    headers = {
        'host': 'user.mypikpak.com',
        'content-length': str(len(json.dumps(body))),
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'referer': 'https://pc.mypikpak.com',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'MainWindow Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'PikPak/2.3.2.4101 Chrome/100.0.4896.160 Electron/18.3.15 Safari/537.36',
        'accept-language': 'zh-CN',
        'content-type': 'application/json',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'x-client-id': 'YvtoWO6GNHiuCl7x',
        'x-client-version': '2.3.2.4101',
        'x-device-id': xid,
        'x-device-model': 'electron%2F18.3.15',
        'x-device-name': 'PC-Electron',
        'x-device-sign': 'wdi10.ce6450a2dc704cd49f0be1c4eca40053xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
        'x-net-work-type': 'NONE',
        'x-os-version': 'Win32',
        'x-platform-version': '1',
        'x-protocol-version': '301',
        'x-provider-name': 'NONE',
        'x-sdk-version': '6.0.0',
        'X-Forwarded-For': str(change_ip)
    }
    response = requests.post(url, json=body, headers=headers)
    response_data = response.json()
    if 'url' in response_data:
        print('初始安全验证中......')
        return response_data
    else:
        print('邮箱或者IP频繁,请更换IP或者稍后重试......')
        raise Exception(response_data.get('error_description', 'Unknown error'))


def get_image(xid, change_ip):
    url = "https://user.mypikpak.com/pzzl/gen"
    header = {'X-Forwarded-For': str(change_ip)}
    params = {
        "deviceid": xid,
        "traceid": ""
    }
    response = requests.get(url, params=params)
    imgs_json = response.json()
    frames = imgs_json["frames"]
    pid = imgs_json['pid']
    traceid = imgs_json['traceid']
    result = {"frames": frames}
    SELECT_ID = pass_verify(xid, pid, traceid, result, )
    print('滑块ID:' + str(SELECT_ID))
    json_data = img_jj(frames, int(SELECT_ID), pid)
    f = json_data['f']
    npac = json_data['ca']
    params = {
        'pid': pid,
        'deviceid': xid,
        'traceid': traceid,
        'f': f,
        'n': npac[0],
        'p': npac[1],
        'a': npac[2],
        'c': npac[3]
    }
    response1 = requests.get(f"https://user.mypikpak.com/pzzl/verify", params=params, headers=header)
    response_data = response1.json()
    result = {'pid': pid, 'traceid': traceid, 'response_data': response_data}
    return result


def get_new_token(result, xid, captcha, change_ip):
    traceid = result['traceid']
    pid = result['pid']
    header = {'X-Forwarded-For': str(change_ip)}
    response2 = requests.get(
        f"https://user.mypikpak.com/credit/v1/report?deviceid={xid}&captcha_token={captcha}&type"
        f"=pzzlSlider&result=0&data={pid}&traceid={traceid}", headers=header)
    response_data = response2.json()
    print('获取验证TOKEN中......')
    return response_data


def verification(captcha_token, xid, mail, change_ip):
    url = 'https://user.mypikpak.com/v1/auth/verification'
    body = {
        "email": mail,
        "target": "ANY",
        "usage": "REGISTER",
        "locale": "zh-CN",
        "client_id": "YvtoWO6GNHiuCl7x"
    }
    headers = {
        'host': 'user.mypikpak.com',
        'content-length': str(len(json.dumps(body))),
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'referer': 'https://pc.mypikpak.com',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'MainWindow Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'PikPak/2.3.2.4101 Chrome/100.0.4896.160 Electron/18.3.15 Safari/537.36',
        'accept-language': 'zh-CN',
        'content-type': 'application/json',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'x-captcha-token': captcha_token,
        'x-client-id': 'YvtoWO6GNHiuCl7x',
        'x-client-version': '2.3.2.4101',
        'x-device-id': xid,
        'x-device-model': 'electron%2F18.3.15',
        'x-device-name': 'PC-Electron',
        'x-device-sign': 'wdi10.ce6450a2dc704cd49f0be1c4eca40053xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
        'x-net-work-type': 'NONE',
        'x-os-version': 'Win32',
        'x-platform-version': '1',
        'x-protocol-version': '301',
        'x-provider-name': 'NONE',
        'x-sdk-version': '6.0.0',
        'X-Forwarded-For': str(change_ip)
    }

    response = requests.post(url, json=body, headers=headers)
    response_data = response.json()
    print('发送验证码中......')
    return response_data


def verify(xid, verification_id, code, change_ip):
    url = 'http://user.mypikpak.com/v1/auth/verification/verify'
    body = {
        "verification_id": verification_id,
        "verification_code": code,
        "client_id": "YvtoWO6GNHiuCl7x"
    }
    headers = {
        'host': 'user.mypikpak.com',
        'content-length': str(len(json.dumps(body))),
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'referer': 'https://pc.mypikpak.com',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'MainWindow Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'PikPak/2.3.2.4101 Chrome/100.0.4896.160 Electron/18.3.15 Safari/537.36',
        'accept-language': 'zh-CN',
        'content-type': 'application/json',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'x-client-id': 'YvtoWO6GNHiuCl7x',
        'x-client-version': '2.3.2.4101',
        'x-device-id': xid,
        'x-device-model': 'electron%2F18.3.15',
        'x-device-name': 'PC-Electron',
        'x-device-sign': 'wdi10.ce6450a2dc704cd49f0be1c4eca40053xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
        'x-net-work-type': 'NONE',
        'x-os-version': 'Win32',
        'x-platform-version': '1',
        'x-protocol-version': '301',
        'x-provider-name': 'NONE',
        'x-sdk-version': '6.0.0',
        'X-Forwarded-For': str(change_ip)
    }
    response = requests.post(url, json=body, headers=headers)
    response_data = response.json()
    print('验证码验证结果中......')
    return response_data


def signup(xid, mail, code, verification_token, change_ip):
    url = 'http://user.mypikpak.com/v1/auth/signup'
    body = {
        "email": mail,
        "verification_code": code,
        "verification_token": verification_token,
        "password": "pw123456",
        "client_id": "YvtoWO6GNHiuCl7x"
    }
    headers = {
        'host': 'user.mypikpak.com',
        'content-length': str(len(json.dumps(body))),
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'referer': 'http://pc.mypikpak.com',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'MainWindow Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'PikPak/2.3.2.4101 Chrome/100.0.4896.160 Electron/18.3.15 Safari/537.36',
        'accept-language': 'zh-CN',
        'content-type': 'application/json',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'x-client-id': 'YvtoWO6GNHiuCl7x',
        'x-client-version': '2.3.2.4101',
        'x-device-id': xid,
        'x-device-model': 'electron%2F18.3.15',
        'x-device-name': 'PC-Electron',
        'x-device-sign': 'wdi10.ce6450a2dc704cd49f0be1c4eca40053xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
        'x-net-work-type': 'NONE',
        'x-os-version': 'Win32',
        'x-platform-version': '1',
        'x-protocol-version': '301',
        'x-provider-name': 'NONE',
        'x-sdk-version': '6.0.0',
        'X-Forwarded-For': str(change_ip)
    }
    response = requests.post(url, json=body, headers=headers)
    response_data = response.json()
    print('验证注册结果中......')
    return response_data


def init1(xid, access_token, sub, sign, t, change_ip):
    url = 'https://user.mypikpak.com/v1/shield/captcha/init'
    body = {
        "client_id": "YvtoWO6GNHiuCl7x",
        "action": "POST:/vip/v1/activity/invite",
        "device_id": xid,
        "captcha_token": access_token,
        "meta": {
            "captcha_sign": "1." + sign,
            "client_version": "undefined",
            "package_name": "mypikpak.com",
            "user_id": sub,
            "timestamp": t
        },
    }
    headers = {
        'host': 'user.mypikpak.com',
        'content-length': str(len(json.dumps(body))),
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN',
        'referer': 'https://pc.mypikpak.com',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'MainWindow Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'PikPak/2.3.2.4101 Chrome/100.0.4896.160 Electron/18.3.15 Safari/537.36',
        'content-type': 'application/json',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'x-client-id': 'YvtoWO6GNHiuCl7x',
        'x-client-version': '2.3.2.4101',
        'x-device-id': xid,
        'x-device-model': 'electron%2F18.3.15',
        'x-device-name': 'PC-Electron',
        'x-device-sign': 'wdi10.ce6450a2dc704cd49f0be1c4eca40053xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
        'x-net-work-type': 'NONE',
        'x-os-version': 'Win32',
        'x-platform-version': '1',
        'x-protocol-version': '301',
        'x-provider-name': 'NONE',
        'x-sdk-version': '6.0.0',
        'X-Forwarded-For': str(change_ip)
    }

    response = requests.post(url, json=body, headers=headers)
    response_data = response.json()
    print('通过二次安全验证中......')
    return response_data


def invite(access_token, captcha_token, xid, change_ip):
    url = 'https://api-drive.mypikpak.com/vip/v1/activity/invite'
    body = {
        "apk_extra": {
            "invite_code": ""
        }
    }
    headers = {
        'host': 'api-drive.mypikpak.com',
        'content-length': str(len(json.dumps(body))),
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN',
        'authorization': 'Bearer ' + access_token,
        'referer': 'https://pc.mypikpak.com',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) PikPak/2.3.2.4101 '
                      'Chrome/100.0.4896.160 Electron/18.3.15 Safari/537.36',
        'content-type': 'application/json',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'x-captcha-token': captcha_token,
        'x-client-id': 'YvtoWO6GNHiuCl7x',
        'x-client-version': '2.3.2.4101',
        'x-device-id': xid,
        'x-system-language': 'zh-CN',
        'X-Forwarded-For': str(change_ip)
    }
    response = requests.post(url, json=body, headers=headers)
    response_data = response.json()
    print('确认邀请')
    return response_data


def init2(xid, access_token, sub, sign, t, change_ip):
    url = 'https://user.mypikpak.com/v1/shield/captcha/init'
    body = {
        "client_id": "YvtoWO6GNHiuCl7x",
        "action": "post:/vip/v1/order/activation-code",
        "device_id": xid,
        "captcha_token": access_token,
        "meta": {
            "captcha_sign": "1." + sign,
            "client_version": "undefined",
            "package_name": "mypikpak.com",
            "user_id": sub,
            "timestamp": t,
        },
    }
    headers = {
        'host': 'user.mypikpak.com',
        'content-length': str(len(json.dumps(body))),
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN',
        'referer': 'https://pc.mypikpak.com',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'MainWindow Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'PikPak/2.3.2.4101 Chrome/100.0.4896.160 Electron/18.3.15 Safari/537.36',
        'content-type': 'application/json',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'x-client-id': 'YvtoWO6GNHiuCl7x',
        'x-client-version': '2.3.2.4101',
        'x-device-id': xid,
        'x-device-model': 'electron%2F18.3.15',
        'x-device-name': 'PC-Electron',
        'x-device-sign': 'wdi10.ce6450a2dc704cd49f0be1c4eca40053xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
        'x-net-work-type': 'NONE',
        'x-os-version': 'Win32',
        'x-platform-version': '1',
        'x-protocol-version': '301',
        'x-provider-name': 'NONE',
        'x-sdk-version': '6.0.0',
        'X-Forwarded-For': str(change_ip)
    }

    response = requests.post(url, json=body, headers=headers)
    response_data = response.json()
    print('通过三次次安全验证中.......')
    return response_data


def activation_code(access_token, captcha, xid, in_code, change_ip):
    url = 'http://api-drive.mypikpak.com/vip/v1/order/activation-code'
    body = {
        "activation_code": in_code,
        "page": "invite"
    }
    headers = {
        'host': 'api-drive.mypikpak.com',
        'content-length': str(len(json.dumps(body))),
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN',
        'authorization': 'Bearer ' + access_token,
        'referer': 'https://pc.mypikpak.com',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) PikPak/2.3.2.4101 '
                      'Chrome/100.0.4896.160 Electron/18.3.15 Safari/537.36',
        'content-type': 'application/json',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'x-captcha-token': captcha,
        'x-client-id': 'YvtoWO6GNHiuCl7x',
        'x-client-version': '2.3.2.4101',
        'x-device-id': xid,
        'x-system-language': 'zh-CN',
        'X-Forwarded-For': str(change_ip)
    }
    response = requests.post(url, json=body, headers=headers)
    response_data = response.json()
    print('开始填写你的邀请码......')
    print(json.dumps(response_data, indent=4))
    return response_data


# ==========================================过验证码函数=========================================
# 定义一个函数，用于图像拼接
def image_assemble(sum_rows, sum_cols, channels, part_num):
    # 初始化一个全零的3维矩阵，用于存储拼接后的图像
    final_matrix = np.zeros((sum_rows, sum_cols, channels), np.uint8)

    # 将part_num中的图像按照指定的位置拼接到final_matrix中
    # 第一排
    final_matrix[0:75, 0:150] = part_num[0]
    final_matrix[0:75, 150:300] = part_num[1]
    final_matrix[0:75, 300:450] = part_num[2]
    final_matrix[0:75, 450:600] = part_num[3]

    # 第二排
    final_matrix[75:150, 0:150] = part_num[4]
    final_matrix[75:150, 150:300] = part_num[5]
    final_matrix[75:150, 300:450] = part_num[6]
    final_matrix[75:150, 450:600] = part_num[7]

    # 第三排
    final_matrix[150:225, 0:150] = part_num[8]
    final_matrix[150:225, 150:300] = part_num[9]
    final_matrix[150:225, 300:450] = part_num[10]
    final_matrix[150:225, 450:600] = part_num[11]

    # 第四排
    final_matrix[225:300, 0:150] = part_num[12]
    final_matrix[225:300, 150:300] = part_num[13]
    final_matrix[225:300, 300:450] = part_num[14]
    final_matrix[225:300, 450:600] = part_num[15]
    # 返回拼接后的图像
    return final_matrix


def getSize(p):
    # 获取输入矩阵的行数、列数和通道数
    sum_rows = p.shape[0]
    sum_cols = p.shape[1]
    channels = p.shape[2]
    return sum_rows, sum_cols, channels


def get_img(deviceid, pid, traceid):
    """
    根据设备id、pid、traceid获取图片
    :param deviceid: 设备id
    :param pid: 图片id
    :param traceid: traceid
    :return: 图片内容
    """
    # 拼接url
    url = 'https://user.mypikpak.com/pzzl/image?deviceid=' + deviceid + '&pid=' + pid + '&traceid=' + traceid
    # 发送get请求
    response = requests.get(url)
    # 返回图片内容
    return response.content


def re_image_assemble(part, img):
    # 获取图片的每一部分
    part1 = img[0:75, 0:150]
    part2 = img[0:75, 150:300]
    part3 = img[0:75, 300:450]
    part4 = img[0:75, 450:600]
    # 第二排
    part5 = img[75:150, 0:150]
    part6 = img[75:150, 150:300]
    part7 = img[75:150, 300:450]
    part8 = img[75:150, 450:600]
    # 第三排
    part9 = img[150:225, 0:150]
    part10 = img[150:225, 150:300]
    part11 = img[150:225, 300:450]
    part12 = img[150:225, 450:600]
    # 第四排
    part13 = img[225:300, 0:150]
    part14 = img[225:300, 150:300]
    part15 = img[225:300, 300:450]
    part16 = img[225:300, 450:600]
    part_nu = []
    for i, j in enumerate(part):
        if j == '0,0':
            part_nu.append(part1)
        if j == '0,1':
            part_nu.append(part5)
        if j == '0,2':
            part_nu.append(part9)
        if j == '0,3':
            part_nu.append(part13)
        if j == '1,0':
            part_nu.append(part2)
        if j == '1,1':
            part_nu.append(part6)
        if j == '1,2':
            part_nu.append(part10)
        if j == '1,3':
            part_nu.append(part14)
        if j == '2,0':
            part_nu.append(part3)
        if j == '2,1':
            part_nu.append(part7)
        if j == '2,2':
            part_nu.append(part11)
        if j == '2,3':
            part_nu.append(part15)
        if j == '3,0':
            part_nu.append(part4)
        if j == '3,1':
            part_nu.append(part8)
        if j == '3,2':
            part_nu.append(part12)
        if j == '3,3':
            part_nu.append(part16)
    return part_nu


# 定义一个函数，用于处理图像
def corp_image(img):
    # 将图像转换为灰度图像
    img2 = img.sum(axis=2)
    # 获取图像的行数和列数
    (row, col) = img2.shape
    # 初始化行和列的上下界
    row_top = 0
    raw_down = 0
    col_top = 0
    col_down = 0
    # 遍历行，找到行上下界
    for r in range(0, row):
        if img2.sum(axis=1)[r] < 740 * col:
            row_top = r
            break

    for r in range(row - 1, 0, -1):
        if img2.sum(axis=1)[r] < 740 * col:
            raw_down = r
            break

    # 遍历列，找到列上下界
    for c in range(0, col):
        if img2.sum(axis=0)[c] < 740 * row:
            col_top = c
            break

    for c in range(col - 1, 0, -1):
        if img2.sum(axis=0)[c] < 740 * row:
            col_down = c
            break

    # 裁剪图像，并返回新的图像
    new_img = img[row_top:raw_down + 1, col_top:col_down + 1, 0:3]
    return new_img


# 定义一个函数，用于获取处理图像
def get_reimage(images):
    # 定义一个空字典，用于存储裁剪后的图像
    cropped_img = {}
    # 遍历images中的每一张图像
    for i in range(16):
        # 对图像进行裁剪
        re_num = corp_image(images[i])
        # 将裁剪后的图像resize为150x75的大小
        cropped_img[i] = cv2.resize(re_num, (150, 75))
    # 返回裁剪后的图像字典
    return cropped_img


def start_pass_verify(sum_rows, sum_cols, channels, img, result, i):
    # 获取结果中的frames部分
    part_1 = result["frames"][i]['matrix'][0]
    part_2 = result["frames"][i]['matrix'][1]
    part_3 = result["frames"][i]['matrix'][2]
    part_4 = result["frames"][i]['matrix'][3]
    # 将四个部分合并
    part = []
    part.extend(part_1)
    part.extend(part_2)
    part.extend(part_3)
    part.extend(part_4)
    # 将合并后的部分重新组装
    start_time = time.time()
    part_num = re_image_assemble(part, img)
    # 获取重新组装后的图片
    part_num = get_reimage(part_num)
    # 将重新组装后的图片按照sum_rows和sum_cols进行组装
    f = image_assemble(sum_rows, sum_cols, channels, part_num)
    # 将组装后的图片转换为灰度图
    gray = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
    # 对灰度图进行边缘检测
    edges = cv2.Canny(gray, 100, 200, apertureSize=3)
    # 对边缘检测后的图片进行霍夫变换
    # lines = cv2.HoughLinesP(edges, 0.001, np.pi / 180, 1, minLineLength=0, maxLineGap=0)
    lsd = cv2.createLineSegmentDetector(0, scale=1.0, sigma_scale=0.6, quant=2.0, ang_th=90, )
    # 执行检测结果
    lines = lsd.detect(edges)[0]
    # 返回线段数量
    return len(lines)


def pass_verify(deviceid, pid, traceid, result):
    # 创建一个进程池,有几核就填几，不要超过5，除非你的内存够大(20g只能开到5，否则内存溢出)，理论上12进程一起2s解决!!!!!
    # replit 是一核，填1，不然卡死!!!!
    pool = Pool(1)
    try:
        # 获取验证码图片
        img = get_img(deviceid, pid, traceid)
        # 获取图片大小
        start_time = time.time()
        img_re = cv2.imdecode(np.frombuffer(img, np.uint8), cv2.IMREAD_COLOR)
        finded = False
        sum_rows, sum_cols, channels = getSize(img_re)
    except Exception as e:
        print(e)
    else:
        # 分配进程
        data_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        start_pass_verify_re = partial(start_pass_verify, sum_rows)
        start_pass_verify_re = partial(start_pass_verify_re, sum_cols)
        start_pass_verify_re = partial(start_pass_verify_re, channels)
        start_pass_verify_re = partial(start_pass_verify_re, img_re)
        start_pass_verify_re = partial(start_pass_verify_re, result)
        len_num = []
        data_i = []
        results = []
        total = trange(len(data_list))
        for data in data_list:
            # 等待任务执行完成
            result = pool.apply_async(start_pass_verify_re, args=(data,), callback=lambda _: total.update(1), )
            data_i.append(data)
            results.append(result)
        pool.close()
        pool.join()
        for data in data_i:
            len_num.append(results[data].get())
        for data, line in enumerate(len_num):
            if line is None:
                num = data
            else:
                if data == 0:
                    num = 0
                    lines = line
                if lines <= line:
                    finded = True
                elif lines > line:
                    lines = line
                    num = data
            data += 1
        print(f'滑块识别时间{time.time() - start_time}')
        print('测试次数', data, '最终状态', finded)
        return num


# 接收验证码接口，可配置自己的邮箱API接口实现自动化
# 邮箱
# 定义一个函数，用于选择邮箱
def choose_email(EMAIL_CHOSSE):
    # 如果EMAIL_CHOSSE等于1，则创建一个EMail对象，并打印出邮箱地址
    if EMAIL_CHOSSE == 1:
        url = 'https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1'
        email = requests.get(url).json()[0]
        print(f'获取邮箱:{email}')
        return email
    # 如果EMAIL_CHOSSE等于2，则调用requests库的post方法，向服务器发送请求，创建一个新的邮箱
    elif EMAIL_CHOSSE == 2:
        json_data = {
            "min_name_length": 10,
            "max_name_length": 10
        }
        url = 'https://api.internal.temp-mail.io/api/v3/email/new'
        response = requests.post(url, json=json_data)
        response_data = response.json()
        mail = response_data['email']
        print(f'获取邮箱:{mail}')
        return mail
    # 如果EMAIL_CHOSSE等于3，则使用str方法将EMail对象转换为字符串，并分割@符号，取第一个值作为用户名，剩余值作为邮箱名
    elif EMAIL_CHOSSE == 3:
        url = 'https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1'
        email = requests.get(url).json()[0]
        name = str(email).split('@')[0]
        # user是邮箱@前面的字符，例如我的是001@gmail.com
        user = '001'
        mail = user + '+' + name + '@gmail.com'
        print(f'获取邮箱:{mail}')
        return mail
    elif EMAIL_CHOSSE == 4:
        url = 'https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1'
        email = requests.get(url).json()[0]
        name = str(email).split('@')[0]
        # user是邮箱@前面的字符，例如我的是001@outlook.com
        user = '001'
        mail = user + '+' + name + '@outlook.com'
        print(f'获取邮箱:{mail}')
        return mail
    # 如果EMAIL_CHOSSE不等于1、2、3、4，则打印出提示信息
    else:
        print('哥们，把你的邮箱接口加上, ok？')
        return None


# 获取邮箱的验证码内容
def get_emailcode(EMAIL_CHOSSE, mail, start_time, max_retries=10, delay=1, ):
    '''
    根据EMAIL_CHOSSE的值获取对应邮箱的验证码
    :param EMAIL_CHOSSE: 1为使用SMTP服务获取验证码，2为使用Temp-mail获取验证码，3为使用Sunls获取验证码，4为手动输入
    :param mail: 邮箱地址
    :param max_retries: 最大重试次数
    :param delay: 每次重试的延迟时间
    :return: 返回获取到的验证码
    '''
    if EMAIL_CHOSSE == 1:
        try:
            demo = str(mail).split('@')[0]
            domain = str(mail).split('@')[1]
            email_id = []
            start_time = time.time()
            url1 = 'https://www.1secmail.com/api/v1/?action=getMessages&login=' + demo + '&domain=' + domain
            while len(email_id) == 0:
                email_id = requests.get(url1).json()
                if time.time() - start_time >= 10:
                    print('No email code found')
                    break
            else:
                email_id = email_id[0]['id']
                url2 = 'https://www.1secmail.com/api/v1/?action=readMessage&login=' + demo + '&domain=' + domain + '&id=' + str(
                    email_id)
                code = requests.get(url2).json()
                rule = r'<h2>(.*?)</h2>'
                code = re.findall(rule, str(code))[0]
                print(f'获取邮箱验证码:{code}')
                return code
        except Exception as e:
            print(e)
    elif EMAIL_CHOSSE == 2:
        retries = 0
        while retries < max_retries:
            url = f'https://api.internal.temp-mail.io/api/v3/email/{mail}/messages'
            response = requests.get(url)
            html = response.json()
            if html:
                text = (html[0])['body_text']
                code = re.search('\\d{6}', text).group()
                print(f'获取邮箱验证码:{code}')
                return code
            else:
                time.sleep(delay)
                retries += 1
        print("获取邮箱邮件内容失败，未收到邮件...")
        return None
    elif EMAIL_CHOSSE == 3:
        try:
            # 这里填你从一号接口中输出的临时邮箱选取作为转发邮箱，不支持多人同时使用，例如我的是123456789@dpptd.com
            response = '123456789@dpptd.com'
            demo = str(response).split('@')[0]
            domain = str(response).split('@')[1]
            email_id = []
            url1 = 'https://www.1secmail.com/api/v1/?action=getMessages&login=' + demo + '&domain=' + domain
            while len(email_id) == 0:
                email_id = requests.get(url1).json()
                struct_time = time.strptime(email_id[0]['date'], "%Y-%m-%d %H:%M:%S")
                timestamp = int(time.mktime(struct_time)) + 8 * 3600
                if int(timestamp) <= start_time:
                    email_id = []
                if time.time() - start_time >= 10:
                    print('No email code found')
                    break
            else:
                if '账户验证通知' in str(email_id):
                    email_id = email_id[0]['id']
                else:
                    print('没找到验证码呢，自己检查一下吧!!')
                url2 = 'https://www.1secmail.com/api/v1/?action=readMessage&login=' + demo + '&domain=' + domain + '&id=' + str(
                    email_id)
                code = requests.get(url2).json()['body']
                rule = r'<h2>(.*?)</h2>'
                code = re.findall(rule, str(code))[0]
                print(code)
                return code
        except Exception as e:
            print(e)
    elif EMAIL_CHOSSE == 4:
        try:
            # 这里填你从一号接口中输出的临时邮箱选取作为转发邮箱，不支持多人同时使用，例如我的是123456789@dpptd.com
            response = '123456789@dpptd.com'
            demo = str(response).split('@')[0]
            domain = str(response).split('@')[1]
            email_id = []
            url1 = 'https://www.1secmail.com/api/v1/?action=getMessages&login=' + demo + '&domain=' + domain
            while len(email_id) == 0:
                email_id = requests.get(url1).json()
                struct_time = time.strptime(email_id[0]['date'], "%Y-%m-%d %H:%M:%S")
                timestamp = int(time.mktime(struct_time)) + 8 * 3600
                if int(timestamp) <= start_time:
                    email_id = []
                if time.time() - start_time >= 10:
                    print('No email code found')
                    break
            else:
                if '账户验证通知' in str(email_id):
                    email_id = email_id[0]['id']
                else:
                    print('没找到验证码呢，自己检查一下吧!!')
                url2 = 'https://www.1secmail.com/api/v1/?action=readMessage&login=' + demo + '&domain=' + domain + '&id=' + str(
                    email_id)
                code = requests.get(url2).json()['body']
                rule = r'<h2>(.*?)</h2>'
                code = re.findall(rule, str(code))[0]
                print(code)
                return code
        except Exception as e:
            print(e)
    else:
        print('哥们，把你的验证码接口加上, ok？')
        return None


def get_change_ip():
    m = random.randint(0, 255)
    n = random.randint(0, 255)
    x = random.randint(0, 255)
    y = random.randint(0, 255)
    randomIP = str(m) + '.' + str(n) + '.' + str(x) + '.' + str(y)
    return randomIP


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)
