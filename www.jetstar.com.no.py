import sys

sys.path.append(".")

import random
from curl_cffi import requests

from pynocaptcha import AkamaiV2Cracker
from utils import __TOKEN__ as USER_TOKEN, __PROXY__starry_keep

version = random.randint(123, 127)
user_agent = random.choice([
    f'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36',
    f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36"
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
    show_ad=False,
    user_token=USER_TOKEN,
    href="https://www.jetstar.com/",
    # 这个 api 会换, 传不传都行, 传的话要记得每次自己去取最新的, 不然传旧的会过不去
    user_agent=user_agent,
    country=country,
    ip=current_ip,
    proxy=proxy,
    debug=True
)

ret = cracker.crack()

if ret:
    extra = cracker.extra()

    session.cookies.update(ret)

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': extra['accept-language'],
        'priority': 'u=0, i',
        'referer': 'https://www.jetstar.com/',
        'sec-ch-ua': extra['sec-ch-ua'],
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': extra['sec-ch-ua-platform'],
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-site',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': extra['user-agent'],
    }

    params = {
        'Currency': 'TWD',
        'adults': '1',
        'children': '0',
        'departuredate1': '2024-08-13',
        'departuredate2': '2024-08-15',
        'destination1': 'CBR',
        'destination2': 'TPE',
        'dotcomFCOutboundArrivalTime': '2024-08-14T15:40:00',
        'dotcomFCOutboundCorrelationId': 'e1e6aa63-8fec-4f76-b044-b52240f87322',
        'dotcomFCOutboundDepartureTime': '2024-08-13T02:40:00',
        'dotcomFCOutboundFare': '15513.23',
        'dotcomFCOutboundFlightId': '161309528',
        'dotcomFCOutboundIncludeMember': 'False',
        'dotcomFCOutboundMemberArrivalTime': '2024-08-14T15:40:00',
        'dotcomFCOutboundMemberCorrelationId': 'd41a3224-1750-4d5f-8bbe-fe76dbc16eea',
        'dotcomFCOutboundMemberDepartureTime': '2024-08-13T02:40:00',
        'dotcomFCOutboundMemberFare': '0',
        'dotcomFCOutboundMemberFlightId': '161309528',
        'dotcomFCOutboundMemberIncludeMember': 'Only',
        'dotcomFCOutboundMemberPriceShown': 'false',
        'dotcomFCOutboundPriceShown': 'true',
        'dotcomFCPricesHidden': 'false',
        'dotcomFCReturnMemberPriceShown': 'false',
        'dotcomFCReturnPriceShown': 'false',
        'infants': '0',
        'origin1': 'TPE',
        'origin2': 'CBR',
    }

    response = session.get(
        'https://booking.jetstar.com/hk/zh/booking/search-flights',
        params=params,
        headers=headers,
    )
    print(response.status_code, response.text)
