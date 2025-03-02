# -*- coding: utf-8 -*-
# @Time    : 2025/3/2 20:46
# @Author  : Chris
# @Email   : 10512@qq.com
# @File    : testnet.lenscan.io.py
# @Software: PyCharm
# -*- coding: UTF-8 -*-


import requests
from pynocaptcha import CloudFlareCracker

# 根据实际情况修改
from utils import __TOKEN__, __PROXY__NST__V6

# 平台注册地址 https://goo.su/i2dKzY 获取令牌
USER_TOKEN = __TOKEN__
# cf和这个平台都支持 ipv6代理 注册地址 https://goo.su/wXmzLan
# 我推荐的这个代理平台是 $0.4 1gb，非常便宜，当然如果你有更便宜的也可以直接用。
proxy = __PROXY__NST__V6

difficulty = "hard"

session = requests.session()
headers = {
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9",
    "content-type": "application/json",
    "priority": "u=1, i",
    "referer": "https://testnet.lenscan.io/faucet",
    "sec-ch-ua": "\"Not(A:Brand\";v=\"99\", \"Google Chrome\";v=\"133\", \"Chromium\";v=\"133\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "trpc-accept": "application/jsonl",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "x-trpc-source": "nextjs-react"
}

resp = requests.post("http://api.nocaptcha.cn/api/wanda/lenscan/universal", headers={
    "User-Token": USER_TOKEN
}, json={
    "difficulty": difficulty,
}).json()
print(resp)

data = resp["data"]
sessionId = data["sessionId"]
moves = data["moves"]

cracker = CloudFlareCracker(
    internal_host=True,
    user_token=USER_TOKEN,
    href="https://testnet.lenscan.io/faucet",
    sitekey="0x4AAAAAAA1z6BHznYZc0TNL",
    debug=False,
    show_ad=False,
    proxy=proxy,
    timeout=60
)
ret = cracker.crack()
print(ret)
token = ret.get("token")

url = "https://testnet.lenscan.io/api/trpc/faucet.claim"

params = {"batch": "1"}

data = {
    "0": {
        "json": {
            "address": "0x1e778b081e145228f6de493ef51b13e3075efee2",
            "cfToken": token,
            "gameChallenge": {
                "sessionId": sessionId,
                "moves": moves
            }
        }
    }
}

response = session.post(url, json=data, headers=headers, params=params, proxies={
    "all": proxy
})

print(response.text)
