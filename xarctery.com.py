import sys

sys.path.append(".")

import asyncio
import random
import re

from curl_cffi import requests
from pynocaptcha import KasadaCdCracker, KasadaCtCracker, PerimeterxCracker

from utils import __TOKEN__ as USER_TOKEN
from utils import __PROXY__idea


async def demo():
    version = 127
    user_agent = [
        # f'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36',
        f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36"
    ]
    href = 'https://arcteryx.com/ca/en/shop/mens/beta-lt-jacket-7301'

    proxy = __PROXY__idea
    print(proxy)

    session = requests.AsyncSession()
    session.proxies.update({
        "all": proxy
    })

    try:
        resp = (await session.get("https://ipinfo.io/json", headers={
            "user-agent": f'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        }, timeout=5)).json()
    except:
        return

    country = resp["country"].lower()
    current_ip = resp["ip"]
    print(country, current_ip)
    #
    # px_cracker = PerimeterxCracker(
    #     user_token=USER_TOKEN,
    #     app_id='PX943r4Fb8',
    #     href=href,
    #     proxy=proxy,
    #     user_agent=user_agent,
    #     country=country,
    #     ip=current_ip,
    #     debug=True,
    # )
    # px_ret = px_cracker.crack()
    #
    # extra = px_cracker.extra()
    #
    # cookies = px_ret["cookies"]
    # session.cookies.update(cookies)

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        # 'accept-language': extra["accept-language"],
        'priority': 'u=0, i',
        'referer': 'https://arcteryx.com/',
        # 'sec-ch-ua': extra["sec-ch-ua"],
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'iframe',
        # 'sec-ch-ua-platform': extra['sec-ch-ua-platform'],
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-site',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.3',
    }

    response = await session.get(
        'https://mcprod.arcteryx.com/149e9513-01fa-4fb0-aad4-566afd725d1b/2d206a39-8ed7-437e-a3be-862e0f06eea3/fp?x-kpsdk-v=j-0.0.0',
        headers=headers,
    )
    if response.status_code not in [429, 200]:
        raise Exception(f"fp status code: {response.status_code}")

    fp_script = response.text

    headers = {
        'accept': '*/*',
        # 'accept-language': extra["accept-language"],
        'priority': 'u=1',
        'referer': 'https://mcprod.arcteryx.com/149e9513-01fa-4fb0-aad4-566afd725d1b/2d206a39-8ed7-437e-a3be-862e0f06eea3/fp?x-kpsdk-v=j-0.0.0',
        # 'sec-ch-ua': extra["sec-ch-ua"],
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'script',
        # 'sec-ch-ua-platform': extra['sec-ch-ua-platform'],
        'sec-fetch-mode': 'no-cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.3',
    }

    uidz = session.cookies.get('KP_UIDz')
    im = re.search(r'x-kpsdk-im=(.*?)"', fp_script)[1]

    params = {
        'KP_UIDz': uidz,
        'x-kpsdk-v': 'j-0.0.0',
        'x-kpsdk-im': im,
    }

    from urllib.parse import urlencode
    ips_url = 'https://mcprod.arcteryx.com/149e9513-01fa-4fb0-aad4-566afd725d1b/2d206a39-8ed7-437e-a3be-862e0f06eea3/ips.js?' + urlencode(
        params)
    ips_resp = await session.get(ips_url, headers=headers)

    cracker = KasadaCtCracker(
        user_token=USER_TOKEN,
        href=href,
        ips_url=ips_url,
        ips_script=ips_resp.text,
        ips_headers={
            k: v for k, v in ips_resp.headers.items()
        },
        country=country,
        ip=current_ip,
        user_agent=user_agent,
        cookies={
            k: v for k, v in response.cookies.items()
        },
        submit=False,
        debug=True,
        auth=True
    )
    ret = cracker.crack()

    # if "post_data" in ret:
    #     headers = {
    #         'accept': '*/*',
    #         'accept-language': extra["accept-language"],
    #         'content-type': 'application/octet-stream',
    #         'origin': 'https://mcprod.arcteryx.com',
    #         'priority': 'u=1, i',
    #         'referer': 'https://mcprod.arcteryx.com/149e9513-01fa-4fb0-aad4-566afd725d1b/2d206a39-8ed7-437e-a3be-862e0f06eea3/fp?x-kpsdk-v=j-0.0.0',
    #         'sec-ch-ua': extra["sec-ch-ua"],
    #         'sec-ch-ua-mobile': '?0',
    #         'sec-fetch-dest': 'empty',
    #         'sec-ch-ua-platform': extra["sec-ch-ua-platform"],
    #         'sec-fetch-mode': 'cors',
    #         'sec-fetch-site': 'same-origin',
    #         'user-agent': extra["user-agent"],
    #         **ret["headers"]
    #     }
    #     import base64
    #     response = await session.post(
    #         'https://mcprod.arcteryx.com/149e9513-01fa-4fb0-aad4-566afd725d1b/2d206a39-8ed7-437e-a3be-862e0f06eea3/tl',
    #         headers=headers,
    #         data=base64.b64decode(ret["post_data"].encode()),
    #     )
    #     print(response.status_code, response.text)
    #
    #     if 'reload' not in response.text:
    #         raise Exception('kasada 验证失败')
    #
    #     kpsdk_ct = response.headers.get('x-kpsdk-ct')
    #     kpsdk_st = int(response.headers.get('x-kpsdk-st'))
    #     kpsdk_cd = KasadaCdCracker(
    #         user_token=USER_TOKEN,
    #         href=href,
    #         st=kpsdk_st,
    #         debug=True,
    #     ).crack()["x-kpsdk-cd"]
    # else:
    #     kpsdk_ct = ret['x-kpsdk-ct']
    #     kpsdk_st = int(ret['x-kpsdk-st'])
    #     kpsdk_cd = ret['x-kpsdk-cd']
    #
    # headers = {
    #     'accept': '*/*',
    #     'accept-language': extra["accept-language"],
    #     'content-type': 'application/json',
    #     'origin': 'https://arcteryx.com',
    #     'referer': 'https://arcteryx.com/',
    #     'sec-ch-ua': extra["sec-ch-ua"],
    #     'sec-ch-ua-mobile': '?0',
    #     'sec-fetch-dest': 'empty',
    #     'sec-ch-ua-platform': extra["sec-ch-ua-platform"],
    #     'sec-fetch-mode': 'cors',
    #     'sec-fetch-site': 'same-site',
    #     'store': 'arcteryx_en',
    #     'user-agent': extra["user-agent"],
    #     'x-country-code': 'ca',
    #     'x-is-checkout': 'false',
    #     'x-jwt': '',
    #     'x-kpsdk-ct': kpsdk_ct,
    #     'x-kpsdk-cd': kpsdk_cd,
    #     'x-kpsdk-v': "j-0.0.0",
    #     'x-px-cookie': '_px2=' + px_ret["cookies"]["_px2"]
    # }
    #
    # json_data = {
    #     'query': 'query gqlGetProductInventoryBySkus($productSkus: [String!]) { products(filter: { sku: { in: $productSkus } }, pageSize: 500) { items { name sku ...on ConfigurableProduct { variants { product { sku quantity_available } } } } } }',
    #     'variables': {
    #         'productSkus': [
    #             'X000007301',
    #         ],
    #     },
    # }
    #
    # response = await session.post('https://mcprod.arcteryx.com/graphql', headers=headers, json=json_data)
    #
    # if response.status_code == 429:
    #     print('kasada 验证失败')
    #     return
    # elif response.status_code == 403:
    #     print('触发 px 验证码')
    #     captcha = response.json()
    #
    #     captcha.update({
    #         "modal": True,
    #         "blockedUrl": 'https://mcprod.arcteryx.com/graphql'
    #     })
    #     px_ret = PerimeterxCracker(
    #         user_token=USER_TOKEN,
    #         href=href,
    #         proxy=proxy,
    #         cookies={
    #             k: v for k, v in session.cookies.items() if "px" in k
    #         },
    #         did=extra["did"],
    #         captcha=captcha,
    #         timeout=120
    #     ).crack()
    #
    #     print(px_ret)
    #     headers.update({
    #         'x-px-cookie': '_px2=' + px_ret["cookies"]["_px2"]
    #     })
    #     session.cookies.update(px_ret["cookies"])
    #
    #     response = await session.post('https://mcprod.arcteryx.com/graphql', headers=headers, json=json_data)
    #     print(response.status_code, response.text)
    #
    #     if response.status_code == 429:
    #         print('kasada 验证失败')
    # else:
    #     print(response.status_code, response.text)
    #     if response.text == '':
    #         return
    #
    # kpsdk_cd = KasadaCdCracker(
    #     user_token=USER_TOKEN,
    #     href=href,
    #     st=kpsdk_st,
    #     debug=True,
    # ).crack()["x-kpsdk-cd"]
    # headers.update({
    #     'x-kpsdk-cd': kpsdk_cd,
    # })
    # response = await session.post('https://mcprod.arcteryx.com/graphql', headers=headers,
    #                               data='{"query":"mutation createEmptyCart { createEmptyCart }","variables":{}}',
    #                               )
    # print(response.status_code, response.text)
    #
    # if response.status_code == 403:
    #     print('触发 px 验证码')
    #     captcha = response.json()
    #
    #     captcha.update({
    #         "modal": True,
    #         "blockedUrl": 'https://mcprod.arcteryx.com/graphql'
    #     })
    #     px_ret = PerimeterxCracker(
    #         user_token=USER_TOKEN,
    #         href=href,
    #         proxy=proxy,
    #         cookies={
    #             k: v for k, v in session.cookies.items() if "px" in k
    #         },
    #         did=extra["did"],
    #         captcha=captcha,
    #         timeout=120,
    #         debug=True
    #     ).crack()
    #
    #     print(px_ret)
    #     headers.update({
    #         'x-px-cookie': '_px2=' + px_ret["cookies"]["_px2"]
    #     })
    #     session.cookies.update(px_ret["cookies"])
    #
    #     response = await session.post('https://mcprod.arcteryx.com/graphql', headers=headers, json=json_data)
    #     print(response.status_code, response.text)
    #
    # await session.close()
    #
    # return response.status_code == 200 and response.text != ''


async def main(num):
    return await asyncio.gather(*[demo() for _ in range(num)])


if __name__ == '__main__':

    import asyncio

    for _ in range(1):
        res = asyncio.run(main(1))
        if not any(res):
            break
