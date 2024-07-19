# -*- coding: utf-8 -*-
# @Time    : 2024/7/19 10:40
# @Author  : Chris
# @Email   : 10512@qq.com
# @File    : sonic_game.py
# @Software: PyCharm
import random

import requests
from loguru import logger
from pynocaptcha import CloudFlareCracker
from utils import __PROXY__starry_keep, __TOKEN__


def claim(address, token, proxy):
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'origin': 'https://faucet.sonic.game',
        'priority': 'u=1, i',
        'referer': 'https://faucet.sonic.game/',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(80, 126)}.0.0.0 Safari/537.36',
    }
    response = None
    for _ in range(3):
        try:
            response = requests.get(
                f'https://faucet-api.sonic.game/airdrop/{address}/1/{token}',
                headers=headers,
                proxies={"https": proxy if proxy.startswith(
                    "http://") else "http://" + proxy},
                verify=False,
                timeout=180)
            break
        except BaseException as e:
            logger.error(e.__repr__())
            continue
    try:
        ret = response.json().get("status", "error")
        logger.critical(ret)
        return ret

    except requests.exceptions.JSONDecodeError:
        ret = response.text
        logger.error(ret)
        return ret


cracker = CloudFlareCracker(
    user_token=__TOKEN__,
    href="https://faucet.sonic.game",
    proxy=__PROXY__starry_keep(),
    sitekey="0x4AAAAAAAc6HG1RMG_8EHSC",
    timeout=120)

resp = cracker.crack()
if resp:
    t = resp.get("token")
    logger.success(claim("5kKwUCMMznyHbJqcNgZy6TsgBdpdiFRXayqhPG9Zw2Uq", t, __PROXY__starry_keep()))
