import re
import sys

sys.path.append(".")

import random

import vthread
from curl_cffi import requests
from pynocaptcha import ShapeV2Cracker
from utils import __TOKEN__, __PROXY__starry_keep


@vthread.pool(3)
def demo(href, request, pkey, script_url=None, script_regexp=None, vmp_url=None, vmp_regexp=None, fast=True,
         verifier=None, proxy=None):
    version = random.randint(123, 126)
    user_agent = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36"

    platform = '"macOS"' if 'Mac' in user_agent else '"Windows"'

    impersonates = [
        "chrome116", "chrome119", "chrome120",
        "edge99", "edge101",
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
        # 'sec-ch-ua': client_hints,
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': platform,
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': user_agent,
    }

    if script_regexp:
        html = session.get(href, headers=headers, verify=False).text
        script_url = re.search(script_regexp, html)[1]

    if not script_url.startswith('http'):
        script_url = origin + script_url

    try:
        script = session.get(script_url, headers=headers, verify=False).text
    except:
        print("初始脚本获取失败")
        return

    if not vmp_url:
        try:
            vmp_url = re.search(vmp_regexp, script)[1]
        except:
            print('vmp 地址获取失败')
            return

    if not vmp_url.startswith('http'):
        vmp_url = origin + vmp_url

    try:
        vmp_script = session.get(vmp_url, headers=headers, verify=False).text
    except:
        print("vmp 获取失败")
        return

    cracker = ShapeV2Cracker(
        user_token=__TOKEN__,
        href=href,
        request=request,
        script_url=script_url,
        script_content=script,
        vmp_url=vmp_url,
        vmp_content=vmp_script,
        pkey=pkey,
        user_agent=user_agent,
        country=country,
        ip=current_ip,
        fast=fast,
        cookies={
            k: v for k, v in session.cookies.items()
        },
        debug=True
    )
    res = cracker.crack()
    # print(res)

    if res:
        if verifier:
            try:
                shape_headers = res[0]
                response = verifier(session, cracker.extra()["sec-ch-ua"], platform, user_agent, impersonate,
                                    shape_headers)
                if response:
                    for k, v in shape_headers.items():
                        if '-a' in k.lower():
                            a_header_value = v
                    print(version, platform, impersonate, country, len(a_header_value), response.status_code,
                          response.text.replace('\n', '').replace('\t', '').replace(' ', '')[:50])
            except:
                import traceback
                traceback.print_exc()
        else:
            print(res)


if __name__ == '__main__':
    def westjet_search(session, client_hints, platform, user_agent, impersonate, shape_headers):
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Origin': 'https://www.westjet.com',
            'Pragma': 'no-cache',
            'Referer': 'https://www.westjet.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': user_agent,
            **shape_headers,
            'sec-ch-ua': client_hints,
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': platform,
        }

        json_data = {
            'appSource': 'widgetRT',
            'bookId': '18-6-2024-1-27-23-95292',
            'currency': 'CAD',
            'currentFlightIndex': 1,
            'guests': [
                {
                    'type': 'adult',
                    'count': '1',
                },
                {
                    'type': 'child',
                    'count': '0',
                },
                {
                    'type': 'infant',
                    'count': '0',
                },
            ],
            'showMemberExclusives': False,
            'trips': [
                {
                    'order': 1,
                    'departure': 'YYC',
                    'arrival': 'ORD',
                    'departureDate': '2024-07-18',
                },
                {
                    'order': 2,
                    'departure': 'ORD',
                    'arrival': 'YYC',
                    'departureDate': '2024-07-25',
                },
            ],
            'promoCode': '',
        }
        try:
            return session.post('https://apiw.westjet.com/ecomm/booktrip/flight-search-api/v1', headers=headers,
                                json=json_data, impersonate=impersonate, verify=False)
        except:
            # import traceback
            # traceback.print_exc()
            return


    for _ in range(1):
        demo(
            href='https://www.westjet.com/shop/flight/0?bookid=18-6-2024-1-27-23-95292&lang=en-CA&urlRef=flight-search-results',
            script_url='https://www.westjet.com/resources/js/wj_common.js',
            vmp_regexp=r'"(https://www\.westjet\.com/resources/js/wj_common\.js\?seed=.*?)"',
            request={
                "url": 'https://apiw.westjet.com/ecomm/booktrip/flight-search-api/v1',
            },
            pkey='Lov30h0l',
            verifier=westjet_search,
            proxy=__PROXY__starry_keep()
        )
