import sys

sys.path.append(".")

import random
import re
from curl_cffi import requests
from pynocaptcha import AkamaiV2Cracker, ReCaptchaUniversalCracker, KasadaCtCracker, KasadaCdCracker
from utils import USER_TOKEN, __PROXY__starry_keep

version = 127
user_agent = random.choice([
    f'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36',
    # f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36"
])

proxy = __PROXY__starry_keep()

session = requests.Session()
session.proxies.update({
    "all": "http://" + proxy
})

resp = session.get("https://ipinfo.io/json", headers={
    "user-agent": f'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
}, timeout=5).json()

country = resp["country"].lower()
current_ip = resp["ip"]

print(country, current_ip)

cracker = AkamaiV2Cracker(
    user_token=USER_TOKEN,
    href="https://www.sephora.com/",
    # 这个东西会变化, 可以不传, 但是传一定要传最新的正确的
    # api="https://www.sephora.com/Px5zZo/uDDY/6v/-p3x/hVchxgWqOlM/f13OpGa9aODrY9/FB0BajANQQk/WnR/BcDx-Cms",
    user_agent=user_agent,
    country=country,
    ip=current_ip,
    proxy=proxy,
    debug=True,
)
ret = cracker.crack()
if ret:
    session.cookies.update(ret)
    extra = cracker.extra()

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': extra['accept-language'],
        'priority': 'u=0, i',
        'referer': 'https://www.sephora.com/',
        'sec-ch-ua': extra['sec-ch-ua'],
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': extra['sec-ch-ua-platform'],
        'sec-fetch-dest': 'iframe',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-site',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': extra['user-agent'],
    }

    fp_url = 'https://www.sephora.com/149e9513-01fa-4fb0-aad4-566afd725d1b/2d206a39-8ed7-437e-a3be-862e0f06eea3/fp?x-kpsdk-v=j-0.0.0'
    response = session.get(
        fp_url,
        headers=headers,
    )
    if response.status_code not in [429, 200]:
        raise Exception(f"fp status code: {response.status_code}")

    fp_script = response.text

    headers = {
        'accept': '*/*',
        'accept-language': extra['accept-language'],
        'priority': 'u=1',
        'referer': fp_url,
        'sec-ch-ua': extra['sec-ch-ua'],
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'script',
        'sec-ch-ua-platform': extra['sec-ch-ua-platform'],
        'sec-fetch-mode': 'no-cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': extra['user-agent'],
    }

    uidz = session.cookies.get('ak_bmsc-kp')
    im = re.search(r'x-kpsdk-im=(.*?)"', fp_script)[1]

    params = {
        'ak_bmsc-kp': uidz,
        'x-kpsdk-v': 'j-0.0.0',
        'x-kpsdk-im': im,
    }

    from urllib.parse import urlencode

    ips_url = 'https://www.sephora.com/149e9513-01fa-4fb0-aad4-566afd725d1b/2d206a39-8ed7-437e-a3be-862e0f06eea3/ips.js?' + urlencode(
        params)
    ips_resp = session.get(ips_url, headers=headers)

    ret = KasadaCtCracker(
        user_token=USER_TOKEN,
        href='https://www.sephora.com/',
        ips_url=ips_url,
        ips_script=ips_resp.text,
        ips_headers={
            k: v for k, v in ips_resp.headers.items()
        },
        user_agent=user_agent,
        submit=False,
        debug=True,
    ).crack()

    headers = {
        'accept': '*/*',
        'accept-language': extra['accept-language'],
        'content-type': 'application/octet-stream',
        'origin': 'https://www.sephora.com',
        'priority': 'u=1, i',
        'referer': fp_url,
        'sec-ch-ua': extra['sec-ch-ua'],
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'empty',
        'sec-ch-ua-platform': extra['sec-ch-ua-platform'],
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': extra['user-agent'],
        **ret["headers"]
    }
    import base64

    response = session.post(
        'https://www.sephora.com/149e9513-01fa-4fb0-aad4-566afd725d1b/2d206a39-8ed7-437e-a3be-862e0f06eea3/tl',
        headers=headers,
        data=base64.b64decode(ret["post_data"].encode()),
    )
    print(response.status_code, response.text)
    if 'reload' not in response.text:
        raise Exception("kasada 验证失败")

    kpsdk_ct = response.headers.get('x-kpsdk-ct')
    kpsdk_st = int(response.headers.get('x-kpsdk-st'))
    kpsdk_cd = KasadaCdCracker(
        user_token=USER_TOKEN,
        href='https://www.sephora.com/',
        st=kpsdk_st,
        debug=True,
    ).crack()["x-kpsdk-cd"]

    headers = {
        'accept': '*/*',
        'accept-language': extra["accept-language"],
        'content-type': 'text/plain;charset=UTF-8',
        'origin': 'https://www.sephora.com',
        'priority': 'u=1, i',
        'referer': 'https://www.sephora.com/beauty/giftcards',
        'sec-ch-ua': extra['sec-ch-ua'],
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': extra['sec-ch-ua-platform'],
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': extra["user-agent"],
        'x-kpsdk-cd': kpsdk_cd,
        'x-kpsdk-ct': kpsdk_ct,
        'x-kpsdk-v': 'j-0.0.0',
    }

    recaptcha_token = ReCaptchaUniversalCracker(
        user_token=USER_TOKEN,
        sitekey='6LdPdW0UAAAAAHNh5_q7pTCQS1lxzqmZ8-k3NDvb',
        referer="https://www.sephora.com/",
        size="invisible",
        title='Gift Cards & eGift Cards | Sephora',
        debug=True,
    ).crack()["token"]

    import json

    data = json.dumps({
        "gcNumber": "6010425892798679",
        "gcPin": "41827169",
        "captchaToken": recaptcha_token
        # "03AFcWeA64nznPWoIWof_zxrvi01PSjkHIkqBPA9EoFNLaxfe5_lg4mj0gdyC7Cu6-pQ_bKF4rgJL35Ej_Uv_DXFjZgIlvYoYVtXheuvq2lg080hYO46Npjh3-PMGoXjJ4AWiLV78_9T_g2B0C9w1hP8lS69a_3EIk_X2ybSWDvL0VMmmHmFfgP03SjRq8Ap0XeDdARVIWbjO2OerrB2uVInnVTz5_LbyyoTX-5BzK9t41TBXGxxj_x_cA1qUigzMMcXQC9Y8P9XOOt5TiUtGgD9DVT3un8sxc4hn4ah1BEsXngkamSQkDA-bdH8iM2GQ2Yrq5mn60TQvEi0dautnL45_uaOhnz1cXRZLTn_0CjlTWxeZ06OV-RUEeEr-RfLxRQnD9UnFhxQ9DPYF5qQClALWJqCikKGgRmCLcp5hlo1ndsZfsGwaSz3FF-f-7bDYDVTUa4hz2tpitgruYJlWAStzZm_UJ5nKUc2FbojhJiXCYF_8GnfLcCExHZ0CRx0bJgTcgige0_he9QhAKAK9HK5bmwZTsvtr7GCUpFRyXJ8LQP85OtL_VEmEbZ0dIwihamcNSS0rn9nqxFwWI332IpAClen2pKmYNJoVSRy50WWLhIQ30E2KgTETDwNFmeoSjT08oiXzX0MsYgL1ntmqXTd4Iqwy6IbtLQdY6pbn1ItvAPndEINI31qcK6V8GjkcpTD3OU_v1qjVwcPuL0QjoFpKwjhpgMmP_p2vKesEJdR6pyRRHPuPZru2hRD1C2mWplprXpEQJkG5u-YWc_0CjwM5HtbS8dRWIE3hglvn6kA64m1aYlQcWjGZw305aer-hzomfMuM1Mm7-1Qb2tumlcLh1WEx_HcPEYj9UL-APNd_nz0J2Vqbz044"
    }, separators=(",", ":"))
    response = session.post('https://www.sephora.com/api/giftcard/balance', headers=headers, data=data)
    print(response.status_code, response.text)
