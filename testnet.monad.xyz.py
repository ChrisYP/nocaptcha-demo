import hashlib
import random
import requests
from pynocaptcha import CloudFlareCracker, TlsV1Cracker

# 平台注册地址 https://www.nocaptcha.io/register?c=qZBx3e
# 新人注册后加QQ群:120639 找管理领取10000点测试点数
# 平台令牌
USER_TOKEN = ""

# 长效(5分钟及以上) 账密代理
proxy = "usr:pwd@ip:port"

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"

href = "https://testnet.monad.xyz/"

resp = requests.post("http://api.nocaptcha.cn/api/wanda/vercel/universal", headers={
    "User-Token": USER_TOKEN
}, json={
    "href": href,
    "user_agent": user_agent,
    "proxy": proxy,
    "timeout": 30,
}).json()
print(resp)

extra = resp["extra"]

headers = {
    'sec-ch-ua': extra['sec-ch-ua'],
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': extra['sec-ch-ua-platform'],
    'upgrade-insecure-requests': '1',
    'user-agent': extra['user-agent'],
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-dest': 'document',
    'referer': href,
    'accept-encoding': 'gzip, deflate, br, zstd',
    'accept-language': extra['accept-language'],
    'cookie': '_vcrcs=' + resp["data"]["_vcrcs"],
    'priority': 'u=0, i'
}

cracker = CloudFlareCracker(
    internal_host=True,
    user_token=USER_TOKEN,
    href="https://testnet.monad.xyz/",
    sitekey="0x4AAAAAAA-3X4Nd7hf3mNGx",
    proxy=proxy,
    debug=True,
    show_ad=False,
    timeout=60
)
ret = cracker.crack()

token = ret.get("token")
a = hashlib.md5(str(random.random()).encode()).hexdigest()
b = hashlib.md5(str(random.random()).encode()).hexdigest()
json_data = {
    'address': f'0x{a}{b[:8]}',
    'visitorId': 'd0455ad5556bab526918e1bd302ac253',
    'cloudFlareResponseToken': token,
}
print(json_data)

res = TlsV1Cracker(
    show_ad=False,
    user_token=USER_TOKEN,
    url="https://testnet.monad.xyz/api/claim",
    method="post",
    headers=headers,
    json=json_data,
    http2=True,
    proxy=proxy,
    debug=True
).crack()
