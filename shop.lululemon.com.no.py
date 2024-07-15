import re
import sys

sys.path.append(".")

import random

from curl_cffi import requests
from pynocaptcha import ShapeCracker
from utils import __TOKEN__, __PROXY__starry_keep


# @vthread.pool(10)
def demo(token, href, request, pkey, script_url=None, script_regexp=None, vmp_url=None, vmp_regexp=None, fast=True,
         verifier=None, proxy=None):
    version = 126
    user_agent = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36"
    # user_agent = f'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36'

    # 自己写跟 ua 匹配的 sec-ch-ua 和 sec-ch-ua-platform, 必须匹配一致, 随机 ua
    client_hints = '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"'
    platform = '"macOS"' if 'Mac' in user_agent else '"Windows"'

    impersonates = [
        "chrome116", "chrome119", "chrome120", "edge99", "edge101",
    ]
    if platform == '"macOS"':
        impersonates += ["safari15_3", "safari15_5", "safari17_0", "safari17_2_ios"]

    impersonate = random.choice(impersonates)

    origin = "/".join(href.split("/")[0:3])

    session = requests.Session()
    session.proxies.update({
        "all": "http://" + proxy
    })

    try:
        resp = session.get("https://ipinfo.io/json", headers={
            "user-agent": user_agent,
        }, timeout=5).json()
    except:
        return

    country = resp["country"].lower()
    current_ip = resp["ip"]

    headers = {
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'priority': 'u=1',
        'referer': href,
        'sec-ch-ua': client_hints,
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': platform,
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': user_agent,
    }
    if script_regexp:
        html = session.get(href, headers=headers, impersonate=impersonate, verify=False).text
        script_url = re.search(script_regexp, html)[1]

    if not script_url.startswith('http'):
        script_url = origin + script_url

    try:
        script = session.get(script_url, headers=headers, impersonate=impersonate, verify=False).text
    except:
        print("初始脚本获取失败")
        return

    if not vmp_url:
        if vmp_regexp:
            try:
                vmp_url = re.search(vmp_regexp, script)[1]
            except:
                print('vmp 地址获取失败')
                return

    vmp_script = None
    if vmp_url:
        if not vmp_url.startswith("http"):
            vmp_url = origin + vmp_url
        try:
            vmp_resp = session.get(vmp_url, headers=headers, impersonate=impersonate, verify=False)
            if vmp_resp.status_code != 200:
                raise Warning("vmp 脚本请求失败")

            vmp_script = vmp_resp.text
        except:
            print("vmp 获取失败")
            return

    res = ShapeCracker(
        user_token=token,
        href=href,
        request=request,
        script_url=script_url,
        script_content=script,
        vmp_url=vmp_url,
        vmp_content=vmp_script,
        pkey=pkey,
        user_agent=user_agent,
        ip=current_ip,
        country=country,
        fast=fast,
        cookies={
            k: v for k, v in session.cookies.items()
        },
        debug=True,
    ).crack()

    if res:
        if verifier:
            try:
                shape_headers = res[0]
                response = verifier(session, client_hints, platform, user_agent, impersonate, shape_headers)
                if response:
                    for k, v in shape_headers.items():
                        if '-a' in k.lower():
                            a_header_value = v
                    print(country, current_ip, version, platform, impersonate, len(a_header_value),
                          response.status_code, response.text.replace('\n', '').replace('\t', '').replace(' ', '')[:30])
            except:
                import traceback
                traceback.print_exc()
        else:
            print(res)
    else:
        print(res["err"])


if __name__ == '__main__':

    def lululemon_login(session, client_hints, platform, user_agent, impersonate, shape_headers):
        headers = {
            'accept': 'application/json',
            'accept-language': 'zh-CN,zh;q=0.9',
            'content-type': 'application/json',
            'origin': 'https://shop.lululemon.com',
            'priority': 'u=1, i',
            'referer': 'https://shop.lululemon.com/',
            'sec-ch-ua': client_hints,
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': platform,
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': user_agent,
            **shape_headers,
            'x-okta-user-agent-extended': 'okta-auth-js/7.4.3',
        }

        json_data = {
            'username': f'tabby{random.randint(110, 100000)}@gmial.com',
            'password': 'sadgbergFD4FV.',
        }
        try:
            response = session.post('https://identity.lululemon.com/api/v1/authn', headers=headers, json=json_data,
                                    impersonate=impersonate)
            return response
        except:
            return


    demo(
        href='https://shop.lululemon.com/account/login',
        script_url='https://shop.lululemon.com/shared/chunk.273c0224d38f1ad8.js?async',
        vmp_regexp=r'"(/shared/chunk\.273c0224d38f1ad8\.js\?seed=.*?)"',
        request={
            "url": 'https://identity.lululemon.com/api/v1/authn',
        },
        pkey='Dwoclkrx',
        verifier=lululemon_login,

        # fast true false 自己调, 风控高了过不去了就改成 false
        fast=True,
        # 改为自己的token以及代理即可
        token=__TOKEN__,
        proxy=__PROXY__starry_keep()
    )
