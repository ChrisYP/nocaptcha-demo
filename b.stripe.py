# -*- coding: utf-8 -*-
# @Time    : 2024/7/15 19:02
# @Author  : Chris
# @Email   : 10512@qq.com
# @File    : b.stripe.com.py
# @Software: PyCharm
import requests
import base64
from urllib.parse import quote
import warnings
from utils import __TOKEN__, __PROXY__starry_keep

warnings.filterwarnings("ignore")


class HcaptchaTester:
    def __init__(self, opts):
        self.opts = opts

    def run(self):
        resp = requests.post(
            "http://api.nocaptcha.io/api/wanda/hcaptcha/universal",
            headers={
                "User-Token": __TOKEN__
            },
            json=self.opts
        )
        json_resp = resp.json()
        return {
            "success": json_resp["status"] == 1,
            "data": json_resp["data"]
        }


def a1(e, t):
    return ''.join([chr(((ord(char) - 32 + t) % 95) + 32) for char in e])


def a2(e):
    def r(e):
        return ''.join([chr(5 ^ ord(char)) for char in e])

    t = e
    n = 3 - (len(t) % 3)
    i = ' ' * n
    encoded = base64.b64encode(r(t + i).encode()).decode()
    return quote(encoded)


def a3(e):
    return a1(a2('{"id":"' + e + '"}'), 11)


for i in range(1):
    try:
        proxy = __PROXY__starry_keep()

        session = requests.Session()
        session.verify = False
        session.proxies = {
            'http': f'http://{proxy}',
            'https': f'http://{proxy}'
        }
        session.headers.update({
            "accept": "application/json",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "zh-CN,zh;q=0.9",
            "origin": "https://js.stripe.com",
            "priority": "u=1, i",
            "referer": "https://js.stripe.com/",
            "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        })

        link = "00geVV063fdN1LGaEJ"
        resp = session.post(
            f"https://merchant-ui-api.stripe.com/payment-links/{link}",
            data="eid=NA&browser_locale=zh-CN&referrer_origin=https%3A%2F%2Ft.co",
            verify=False
        )

        session_id = resp.json()["session_id"]
        guid, muid, sid = [
            "edd5d662-3e64-4a3e-8c92-7f4e39d95b9ed664c7",
            "8b28984d-5ed3-4261-8ee1-2b528b8f3fb467280f",
            "2168d691-30fa-4d08-bff9-b1a29f7c4990f6105e"
        ]
        resp = session.get(f"https://merchant-ui-api.stripe.com/payment-links/{link}")
        key = resp.json()["key"]

        resp = session.post(
            f"https://api.stripe.com/v1/payment_pages/{session_id}/init",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=f"key={key}&eid=NA&browser_locale=zh-CN&redirect_type=url"
        )
        init_checksum = resp.json()["init_checksum"]

        resp = session.post(
            f"https://api.stripe.com/v1/payment_pages/{session_id}",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=f"eid=NA&tax_region[country]=JP&key={key}"
        )
        json_resp = resp.json()
        unit_amount = json_resp["line_item_group"]["line_items"][0]["price"]["unit_amount"]
        rqdata1 = json_resp["rqdata"]
        site_key1 = json_resp["site_key"]

        t = None
        while True:
            t = HcaptchaTester({
                "sitekey": site_key1,
                "referer": "https://b.stripecdn.com/stripethirdparty-srv/assets/v20.25/HCaptchaInvisible.html?id=e116ac03-cb9a-4809-b411-7964413501cd&origin=https%3A%2F%2Fjs.stripe.com",
                "rqdata": rqdata1,
                "proxy": proxy,
                "deviceHash": "7462ae5e0370097537112553f7c1cbfe",
                "internal": False,
                "local": False,
                "need_ekey": True
            }).run()
            if t["success"]:
                break

        resp = session.post(
            f"https://api.stripe.com/v1/consumers/sessions/lookup",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=f"request_surface=web_checkout&amount=15935&currency=hkd&email_address=icloud%40wkchi.com&email_source=user_action&session_id={session_id}&key={key}"
        )
        resp = session.get(f"https://api.stripe.com/edge-internal/card-metadata?key={key}&bin_prefix=518868")

        resp = session.post(
            f"https://api.stripe.com/v1/payment_methods",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=f"type=card&card[number]=1111110437556804&card[cvc]=222&card[exp_month]=04&card[exp_year]=28&billing_details[name]=Mildred%C2%A0M%C2%A0Hollifield&billing_details[email]=icloud%40wkchi.com&billing_details[address][country]=HK&guid={guid}&muid={muid}&sid={sid}&key={key}&payment_user_agent=stripe.js%2Fdb3292dc43%3B+stripe-js-v3%2Fdb3292dc43%3B+payment-link%3B+checkout"
        )
        pm_id = resp.json()["id"]

        resp = session.post(
            f"https://api.stripe.com/v1/payment_pages/{session_id}/confirm",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=f"eid=NA&payment_method={pm_id}&expected_amount={unit_amount}&last_displayed_line_item_group_details[subtotal]={unit_amount}&last_displayed_line_item_group_details[total_exclusive_tax]=0&last_displayed_line_item_group_details[total_inclusive_tax]=0&last_displayed_line_item_group_details[total_discount_amount]=0&last_displayed_line_item_group_details[shipping_rate_amount]=0&expected_payment_method_type=card&guid={guid}&muid={muid}&sid={sid}&key={key}&version=db3292dc43&init_checksum={init_checksum}&js_checksum={quote(a3(pm_id))}&passive_captcha_token={t['data']['generated_pass_UUID']}&passive_captcha_ekey={t['data'].get('ekey', '')}&rv_timestamp=qto%3En%3CQ%3DU%26CyY%26%60%3EX%5Er%3CYNr%3CYN%60%3CY_C%3CY_C%3CY%5E%60zY_%60%3CY%5En%7BU%3Eo%26U%26Cydbn%3DY%26%23%3Edbd%24Yu%60%3CYRosdRL%3CXOn%24Y%26Qveu%60%3EY_%60%24XbLCXbP%24X%26%23%25Ytn%7BU%3Ee%26U%26CyYu%5CCdRYxX_%3B%23%5B_%5C%3CY%3DQrXu%3B%3Be%26oy%5B_Uy%5BO%3B%3CY%26%60%26d%3DMrXxeu%5B_esd_X%23d%26YsdOT%3EeOQre%26%23%3D%5B_%5CCX_UuX%26%24yYNo%3FU%5E%60w"
        )
        if "error" in resp.json():
            print(resp.json()["error"])
            continue

        json_resp = resp.json()
        payment_intent = json_resp["payment_intent"]
        id = payment_intent["id"]
        client_secret = payment_intent["client_secret"]
        rqdata = payment_intent["next_action"]["use_stripe_sdk"]["stripe_js"]["rqdata"]

        t = None
        while True:
            t = HcaptchaTester({
                "sitekey": "c7faac4c-1cd7-4b1b-b2d4-42ba98d09c7a",
                "referer": "https://b.stripecdn.com/stripethirdparty-srv/assets/v20.25/HCaptchaInvisible.html?id=e116ac03-cb9a-4809-b411-7964413501cd&origin=https%3A%2F%2Fjs.stripe.com",
                "rqdata": rqdata,
                "proxy": proxy,
                "deviceHash": "7462ae5e0370097537112553f7c1cbfe",
                "internal": False,
                "local": False,
            }).run()
            if t["success"]:
                break

        resp = requests.post(
            f"https://api.stripe.com/v1/payment_intents/{id}/verify_challenge",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=f"challenge_response_token={t['data']['generated_pass_UUID']}&challenge_response_ekey=&client_secret={client_secret}&key={key}"
        )
        print(resp.text)

    except Exception as error:
        print(error)
