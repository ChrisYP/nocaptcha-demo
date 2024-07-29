import sys

sys.path.append(".")

from curl_cffi import requests
from pynocaptcha import AkamaiV2Cracker
from utils import USER_TOKEN

# proxy = "127.0.0.1:7890"

session = requests.Session()
session.proxies.update({
    # "all": "http://" + proxy
})

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
}

href = 'https://www.eurowings.com/en/booking/flights/flight-search.html?isReward=false&destination=ALC&origin=BHX&source=web&triptype=r&origins=BHX&fromdate=2024-08-12&todate=2024-09-10&adults=1&children=0&infants=0&lng=en-GB'
response = session.get(href, headers=headers)
print(response.status_code, response.text)

if 'sec-cpt' in response.text:
    res = AkamaiV2Cracker(
        user_token=USER_TOKEN,
        href=href,
        sec_cpt_html=response.text,
        cookies={
            "sec_cpt": session.cookies.get("sec_cpt")
        },
        debug=True,
    ).crack()

    session.cookies.clear()
    session.cookies.update(res)

cracker = AkamaiV2Cracker(
    user_token=USER_TOKEN,
    href=href,
    cookies={
        k: v for k, v in session.cookies.items()
    },
    telemetry=True,
    debug=True
)

ret = cracker.crack()

extra = cracker.extra()
headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-GB,en;q=0.9',
    'akamai-bm-telemetry': ret["telemetry"],
    'content-type': 'text/plain;charset=UTF-8',
    'origin': 'https://www.eurowings.com',
    'priority': 'u=1, i',
    'referer': 'https://www.eurowings.com/en/booking/flights/flight-search.html?isReward=false&destination=ALC&origin=BHX&source=web&triptype=r&origins=BHX&fromdate=2024-08-12&todate=2024-09-10&adults=1&children=0&infants=0&lng=en-GB',
    'sec-ch-ua': extra["sec-ch-ua"],
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': extra["sec-ch-ua-platform"],
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': extra["user-agent"],
    'x-csrf-token': '{683fc78c93555ed7a6a26af204cb44ab8754c3b61145e284f6901941582a46291490c75bcc7a365f4f58cd87fbbd3736db3b7cb8b6b5894e23b22db9e3d320f89aa2c74de3c43219b50582ffd4692c36ce79a9b460d3f12ac01f63ce84cc9960}',
}

params = {
    'action': 'QUERY_FLIGHT_DATA',
}

data = '{"_payload":{"_type":"UPDATE_COMPONENT","_updates":[{"_type":"ew/components/booking/flightselect","_path":"/content/eurowings/en/booking/flights/flight-search/book-flights/select/jcr:content/main/flightselect","_action":"QUERY_FLIGHT_DATA","_parameters":{"origin":"BHX","destination":"ALC","outwardDate":"2024-08-12","adultCount":1,"returnDate":"2024-09-10","tripType":"ROUND_TRIP"}}]}}'

response = session.post(
    'https://www.eurowings.com/en/booking/flights/flight-search/book-flights/select.booking.json',
    params=params,
    headers=headers,
    data=data,
)
print(response.status_code, response.text)
