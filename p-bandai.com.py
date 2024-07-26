

import re
import sys

sys.path.append(".")

import asyncio
import random

from curl_cffi import requests
from pynocaptcha import ShapeV2Cracker
from utils import __TOKEN__ as USER_TOKEN


# @vthread.pool(10)
async def demo(href, request, pkey, script_url=None, script_regexp=None, vmp_url=None, vmp_regexp=None, fast=True, verifier=None, cookies={}, proxy=None):

    version = 126
    user_agent = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36"
    
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
    if proxy:
        session.proxies.update({
            "all": "http://" + proxy
        })
    session.cookies.update(cookies)

    try:
        resp = session.get("https://ipinfo.io/json", headers={
            "user-agent": f'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        }, timeout=5).json()
    except:
        # print('代理失效')
        return

    country = resp["country"].lower()
    current_ip = resp["ip"]

    headers = {
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9',
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

    cracker = ShapeV2Cracker(
        user_token=USER_TOKEN,
        href=href,
        request=request,
        script_url=script_url,
        script_content=script,
        vmp_url=vmp_url,
        vmp_content=vmp_script,
        pkey=pkey,
        user_agent=user_agent,
        submit=False,
        ip=current_ip,
        country=country,
        fast=fast,
        cookies={
            "dtJ5tPjd": session.cookies.get("dtJ5tPjd")
        },
        debug=True
    )
    res = cracker.crack()
    extra = cracker.extra()

    if res:
        if verifier:
            try:
                shape_headers = res[0]
                response = verifier(session, extra, impersonate, shape_headers)
                if response:
                    for k, v in shape_headers.items():
                        if '-a' in k.lower():
                            a_header_value = v
                    print(country, current_ip, version, platform, impersonate, len(a_header_value), response.status_code, response.text.replace('\n', '').replace('\t', '').replace(' ', '')[:30])
                # else:
                    # print('验证错误')
            except:
                import traceback
                traceback.print_exc()
        else:
            print(res)


if __name__ == '__main__':
    def baidai_login(session, extra, impersonate, shape_headers):
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': extra["accept-language"],
            'content-type': 'application/x-www-form-urlencoded',
            # 'cookie': 'OptanonConsent=isGpcEnabled=0&datestamp=Thu+Jul+25+2024+12%3A38%3A18+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=202406.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&genVendors=&consentId=225446d3-2762-48e7-9a19-424f32f8bc10&interactionCount=1&isAnonUser=1&landingPath=https%3A%2F%2Fp-bandai.com%2Fhk%2Flogin&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1; JSESSIONID=5CC3B1C88629B591E8788FC5F24AD043; defaultSite=hk; ktlvDW7IG5ClOcxYTbmY=a; ABTastySession=mrasn=&lp=https%253A%252F%252Fp-bandai.com%252Fhk%252Flogin; _clck=14kp0wy%7C2%7Cfnr%7C0%7C1667; _gcl_au=1.1.1837661181.1721882142; _gid=GA1.2.1209416569.1721882143; __rtbh.lid=%7B%22eventType%22%3A%22lid%22%2C%22id%22%3A%22e0ZvLPeb3kZZVYCqnCs0%22%7D; script_flag=43750084-1903-4af0-9a96-bab2b72038ea; url_flag=https://p-bandai.com/hk/login; pgmodal2=true; __ulfpc=202407251235439653; _fbp=fb.1.1721882144088.50199951674841731; FPID=FPID2.2.zVTZtw%2B9t4eOr3CuLUY2gFYMxdDRQcVwUekxRxIqMH4%3D.1721882143; FPLC=uxqHExcDpq%2FwD5QQKENfebrV2lIIZgYu9FRkq0MDC6DOdCziyxL%2FetGhCX4mphOAPhaQtIGrJ%2FRg6b2XbLcF%2B4H4rS9Kisds%2FU9efvXcKY1BagcBY0369%2Bm0JpJwWA%3D%3D; recommendUser=KW91FssHeiCKbCpB2RtZnmDnkVFDqBWsgcvK88w7GlxTS3e8ui; dtJ5tPjd=A85NLOiQAQAA88OcBPYiml27qfqS0eVsCZqv5zHr0KJdWNq7Pxqx_LVLkWKAAWj5rnuucuopwH9eCOfvosJeCA|1|0|366467f0e913857a136a137049868fa7b92c26a7; AWSALB=1NUE5Y3NzuP6bF/LYyRzqMlCt90WHo12eK7t+yMhUm9orwATnVtf3ra7gUFvELhik4POC5El/u4CXKxJDmqQOimEKV/xNklpUaXz/iLWO4XEbJIOAfika6hZK2h0; AWSALBCORS=1NUE5Y3NzuP6bF/LYyRzqMlCt90WHo12eK7t+yMhUm9orwATnVtf3ra7gUFvELhik4POC5El/u4CXKxJDmqQOimEKV/xNklpUaXz/iLWO4XEbJIOAfika6hZK2h0; ABTasty=uid=vs658zyd0wajeqs7&fst=1721882137721&pst=-1&cst=1721882137721&ns=1&pvt=2&pvis=2&th=; _ga_67MWHF65HK=GS1.1.1721882142.1.1.1721882299.0.0.1341660271; _ga_X05EWL8N9Q=GS1.1.1721882143.1.1.1721882299.54.0.0; FPGSID=1.1721882144.1721882300.G-67MWHF65HK.vNtvP2vzcL3XpA_VZVzcXQ; _uetsid=5a8368104a3f11efb036e9af035388bf; _uetvid=5a838d504a3f11ef8132157f627491a9; _clsk=1r0gaso%7C1721882300631%7C2%7C1%7Cs.clarity.ms%2Fcollect; _ga_X5PY18JBQR=GS1.1.1721882144.1.1.1721882302.51.0.0; _ga=GA1.1.930467927.1721882143',
            'origin': 'https://p-bandai.com',
            'priority': 'u=0, i',
            'referer': 'https://p-bandai.com/hk/login',
            'sec-ch-ua': extra["sec-ch-ua"],
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': extra['sec-ch-ua-platform'],
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': extra['user-agent'],
        }

        data = {
            # 'p8kOmysnbc-a': 'tqPXwebTB-8dgMZMy5O5K5iWk8yxaEtGkUHa3KQ6FqSRpG28VV9UXk=D36h7XgRx_kKWcSLJLToKHBo0xiaYp2ZJ0XAPzyx=yGVTOpg48YWFElQH0_Zht-B4AdLTYSQbXZclMcK4duXgoabMs_RoYG_9Lwx0ZjMA1ToIP3Hz7WVk6wh8Os=bha2DWr90P7GSrC39NMuxmogYKhfVSr3iETuSMCdJzVHYzb12pwmePNgV_liYxAeps2_tvkiI9Gjh6bsX9C_rCVQIfTuodpO0U=ia1WGOz9RMDZfFJsrJ4YiAGD6tCU8xrZC7_9LNHOoLKRy0Ju2iYBws8gTmzbA=hJ6hKuP2CCks45bsG5saS2pJY62NUs5cMg1HLr8-_xdtvCgwvMaEgUbP3ktER5UeQxqrEcWIgQw2DfCzphKpKoef51Nme8YIHZEZv1Mkft2XB9QJD5_qjSc6zsktW1RPQdwVtHog50MkMjd3fPLb-jL96G=DP8jT9yhJKRgKvwkDyrBQQR08fVsJLtfqT17mvTf7uykFigJT21yy_=MY5QqKTz-dIzdGwiL5l4r6aA7874Lebz8gLkxzuF2_5HrY4Ef_qbyv=WG3DI-YfUa8gP74Vwq13Ap-m0rW-SCHwQ3X7iBONave04J_vGMEfcHkJyHgWfKuKCXAB80tExDGvNoizYePE-ZgFqTaWBCcey=tGu5iJ0_kl6HXBVWs7SrC5=7artWmJDR6sWa-DeQkF1Gfyk8GP8XqCSmRvNBOxFl7_j8uWzmN4dSQSb5dASI40ptV=7gTpme1o-Bw1jUgwCwC-sCVH0d0JO0o3auMAE75LOsgXrWLoEPWO89ucogKiZ91rgxi1a7PlFw_pMWOt=8HdsJKs4qwzXFbLg=6NuVRuCqUxSO3awHQX1EQ8he3Kz3rGz4mpBCfsNxKRZm-1bXoo=aoELG=yK9ueEKV-gZw4GS=GwD7rXqSCOZI6NsMm_mUf-sb_F4dCKk6R3JbQGpDcxZoBza603O5Y5eTB-GhquhSAuYD1WiCIvaZhtdQy=uqkya2tu18_GbaD1dwzF1LATqFRJopQZzI9R-evcOp8by6WAg0rLL0y=uyCOD0LsQW7Qls1Tkwacr3CRp_kp90hTKrw7XgCeiUM_3KzLAHfj=s=iGQ3Sem2byRmAXO3DNVgZMk7mCYxoum=t880o67QhuMqHCkew1OxrGqA9=0U_2gvLNhA-i6bHHeBbrfwsxp8gbIMcWa74k0ov=TB=1=r919ucjqM45C7MtKDdyOXEd-t0Y3j3_UNtMg2QiVIIRrImsM0RVRDcRGWFWHFv7iWc57TKqPCeNBB_iaWbYYix7blLpG0N9kLAdHCEk_tMO9ULHpFjEczD9HScRzX3B8roP7KP4dp6c1i2ytZuCLSW68oB7G85As6SkF5FjzYQlP6LYoNa79y3itHIlM_dN51iZvs-sW_JO=3Dt=8dy_ZIlaDKfRaEL0l5ypvU-UHztvJHuHsVsc1woXhaZu4s5gzf9rxP0wNCqkvfzT_cs7YzDlrlRACljlrySv9MEPurc=ib9WyVw_W1GS=DBk3OSWi__xyKf=LY6xSGXmzkrkj__qCD65AYz0iTz4M5lZ3TiFC5Yz5h7NIoS0s5ERl0QgFIL7MoHaZWC0YSCRQUTO8afNGNyH4aT4GPxp2Rm-N76etwLpWYmVYtE4CrbrNJVotLv6ZCbsc__8UXhRwRXgfGC6ajaqG0SGDgF32Z20P7mUg4gUzmJLVJzE6LhOU-zS76q9k72JVOp7H7hkRUaUmFG7qmdMdTLL2Kizw-j7yigE05odjZcvj-WlGhX2kchxQfyohxUNliAWN=UJ6CFjKiU4TpJ9wMs-Y==53XlUFPk8Bh-_giyGg9DJGKTO0JSHXvFAzkDoWNMoZEJg0f__bN3k6MmQYF_JcK2RNHu8lMlSII-qwQmptoqwYZhibddFOeSfoEt4QXZHUpewwWq3FAW3b2UscjMihRdm6Iy97LpomIJ0-oDiUUWjAGVAuqpv55lUCH25CtqDPKsy4MOAwwQ1yrLtMC4gYP4iS4_EHJ0J9J5z1IB-ql3HZWCoi56tC--MLrTzj1qMAASqSGj6AkuZmJmr4lrLeubeu5WDpelJ6Zw7Y1IxsQm8_3U9ajFgro83QTTGaFLroPzcAb5eoZCdOh2tDf7=jjbzuIPMHa2YiT_7KqPlfB8h5h87cGrfvhbV0_JX3hAIrwA91dXayObkv-RF89SIC0xT9eebsbd37cSmwYMd-Eczx3KCPz6mWO09TmDGd_wH6=ANXO0xVN6haxAS30WlsVXN3XobBWp=y-UD6EMJP=pRsshS9kN4kMM0NHQCzLRl7tYoQ7y==grG2spy1bwyVmTHAAltgDO6l0gwlDx=I0VXJyf5k8FYqgo2wRUKbfOZOeEdMBXXiDkYFez_LUWp9hCHXEwtQQDdgptqzCbDXVYwlTdIT9h=ToPw48fK3SZd4p597XP6TYd5PlJU0ImhCUcbOh_oJyK2RHpoiZaL_=5aT02WKlfiUvjYuC5bpS8-VzXe9Zzk3TD1luw7YkDbVS-8MwUNseF3v8b_7Dktr_jKFHQNBFM5UM4__9eJ55sw8ZTzNNkr1bk-7cUwcafT7aGPd0aRkDPP-d4wawyK8Il6PraKzZi3uMN5pXmddrkv0P3swZVsWbM-ZmB5X7eqFONQE4XcxEOu_UIvbMIVzhYzg1emqeY63yKAYuJuzqjEBAleKSdaT60f1o9-MVG=CmGEViM88V6uDNd7c3_FARkx-fJafyD8HsWqM6B6QRNxbQrOqiNBy8azSUU9AmgH74g8x=MmQyClzEdaZUoCKQ=wTtvQgUg1iEwqhWvwbaf1=HRP7_DCfJKexGqiRa27wWd5-5wSJc8=eBl3ftkp=p-geZEjUeRc1yx4kHtf_Fd5CCg-FsXksEpg8tLOV4WCHpOYgYZ0QKqqHsKD6ONkflJxdMXrjQAWlmkmoNi0UT5gHGIL0zJ12PYiQb_zwfRXfKODx4ROhJzLd1v0ozEIl99PJUMI5ii0z5A-oq0RkGTAkQHA93=-1JySzzDT0Fg1PJ-AjdIsgDmM56QRxxqqtMwR05oGbU24Uc-SW3BqjL1y2glI9_hf2s9uG=yDKxboN6g1NZhrtG54WpLTAeMy1KLUNIv85-Uz6OQLR5cgGA=0JNFa6sBRqCAS4P6LuMXajECUtCzpvjs2ahet4VlwtitQawq2Bx-1FS5dvysaSL9xL42L6dI3bXFHH5Hi6f00Ns5lC=-w3ICxe_pt=AqDpYk_=4dzR0qR3aPSKNl6l28PThl0zs2GP8BiQqGllygJtb8thXINEkD-X_SuYkxveufRxbmzDdfgH5fC43W6jONmFOZ3u-aK_OtEMPS3yoh33OihrkpAE1P7gZAA6daJkfhfExOoAVmF=Xz5vX=3mSD5HT3T__u26xloFDqQ=wUZje8SbiYmgQ7wUBWbi4GAw=YX2vpMKFOQ5CvPg=PUzpBFg5gQmyAxpT_4YMMFMQfdx6e9ygxSsJXkrt1CzV_Ecs6UFMvAGzyHoH0w2ZEK=hNc9jOqIZ6d_E4JjpCObP84Kd1YcFP-=etIvox=8bl=DPvpJTMFo0OWyyMpvGoSx7PLX3PGD41vIzfh8_eLm8kMi-hYaOMoMHSBq3A-p1EtTPFDZVxF93zVNcfhleetQT25rKbVZKeflakD519_rKJ4BrxFZwvlosidG8POlho5aU9VDQivdS7-Ipv=TF-Bl2-7qK6THRkSBQ1HYN0w2kfJgLsNxukV0sc5LyJGYKPBksgDwL4lNZUOAUZipJEVkJdS0gd6b35ACvM7xv1xLyD71kYhtwyBOz6gZgRj-jVtlJlsAXATiXv5ZAtgtQKy9r32EWGBGA1QDO6lchBVyRwypFL7tS6PpWab3vVrNq=R=rmKuvz8xiGpWO9V6-RCK=WYQSlAKDYHh-tDt9CKim8y2x4Si-fVIfMM95_bQHDI4XSmZq0ABqMkEwqT182xKTUV6VIUYsza6fkxg49xOzRALssdyRkUaEWmCTZeDIMUe2ujwkah2RDLb28W5aJ9I4KDo9SEe5LPWhM5dC7tiM4lWoRiroEsmZ7bSO-ZGOfOt8A=s-xlA3rHxphbo9Ql6yZhj60gym9j9pILHsjktrD=wPlNC7_R3EG8gvH6k08uWUAvqEAFdFSQ725atKv0fB1zJD51Upw168-0L9QEB74PAIEx2EMCrLbTi68E3PgiEN1eess-UH1crw4a3jFHv3hcZzz8W0v=vgGFVfmM8Zb=0Xbf8dlzYu6O=tLRzBHMNi9MCzNkpYazw4KUZ2ocdqxQPLG=_iBD-kPguCCgvu-R=Zxz5z9OOu2weAip9lxL9Zq3ChsLgKVNz8fx=8_OjLWC=Cq61eeKJOW_DMr4P7-6UIbuBI88r9T1xBMapJGPYAbMLuWH99HAL9JxNyb2FESUm20bb0u_Tk8t5Nhvdb7d91C=FoQJbrbx48Ts7kxPUfmFvXcH5d89QiY9KZeiq_pmOsrwaDMUezTEbsFtdAmS6Cq34ES6o4JLNocuTaGoWg__hj6Ryt2-9bzaax6fVTgdkjVsbI6Ya=MEBcwFYz6wK-vVqolyWaJEau6Ujqf-1HWX1uqiLK=_cjN3RzStCIg0Xvb5DkDIVY-RWfkB9Sy-62RGop_iiUAxS3VrhZ0B545T3=624qXhtrHHHOqCqkHFoVC=X9tAwLZvSEfYE-6L4Qb7stpeN4Wd-cmQBOwV23osxS04lPy4UT6Ehfqyi8I899R8Glrt-vtZy1Qgq6OMUXCrRoI=DOlW5gkTfzpuTWZBr4b=78xaY9QlmCkbYoai3gYZt0sZYcQR3B5tdHqmLW_3AzdOK4-kz4jOXWdqtw-Mto399S-RG3XSxtJHc8Kl79E8X=xbx00W1YmxNj46tu2VFuBvs0bVTVYWya0eRX-xzh9=cmr4Xp9ZScbOch6=RKyzXwaNCrOxVU5aY9YQduRI_UFM2bDiltk-GlHgJc=jorhw0FDqVGfyrct49UoAgrRhjEPdiyJSo7Xhl1Aa5-kfkPPI8fHZH2JAO5PCtI=fujfZjELNbl7tfEyrrEzdo0Ojmf9psmEFmPho2b_Ge5zlrehXmHFLJXA4VNhoY8RLKTT_Yaa1hfSdRi2KBHKIKplxuXPdw7qVRHaXBjP-yQK8uF9aocv0rMQxPmELXj3qdu9lBg6mUWwig_jczG6sWrijWNqV=KEfyJ9AGwL=sXyUL8GYK-hMyQACiuijbXouH8PrdIDlpmPHMR47xlZ=rbMeoNjrfq1qc-y9Usv7yWQo0-Uzy0NO7O5yY56hY2HrR_1uwQMf2pEHlPBxlPcXaF0YBFtcxi_PuqsZDhB1bRyPuuz9B2bFcRm1NeqX1L1ZqjC_TcakKOo2T7jJZaQbA7zDxMXKmSJptK7hAw3O2csFx446oB4Mz8s3DOVdZxQW6QfKj=jp-fG1kgVug-FWjEzOTNMxxt--NQL6EclKAltkt3xix4_QrvXQ=uTrtVp9f=x=Tv6FVU9CPOh3tUGcLB0cwtr4UmI_IT1TLWJBrxCFP0GXkm3fy-2eKXWjLikILI4OgsmRs=o28qlFO2v0-EjNpE5PTFlbWlyi5SMH0Xck9pUTbQvjiKgyP6J9DP0JKbHCr-hQa3W0p9QRAoFe6WwJPsQqR33V-kWO61gztsRsSOuBr=-XBdLD9EzQhwbSzxES0CRSq1XfA8ZJIJ22BEVmPHBPaB4DJ34CDdF7K1yqdFDpC4eECMf975TmtCJx6RRs30JZ_HtALySxGBt_MB39Yl2hCbHZURgSL=Laou2Xh9fiium6BkQq-A9E=rk1HyQ9qR0FzdFXRy4eTh8E0iYBAcuSNhjKWYTv4w7ejdDO-j7_N13_QjZ-8=g=W_GQ-CsGPAg1r3TcHv=yq-tvASFmBJDp1RiDK572GsSEfqvB09cy35hhZ6aUNt4tWfam9a1M-0OCJutm-P=G1MY681LY2Q4h_tcf8ErxhLhIxsfehb32b043WZxTXx44itNU5PPsfZrqu=QmGbTAJHyek5Wz_DFR2TYBI6sNaBCmWy4P5lg3IWWN=6SpAo_Pz44IzujxAg6VkRSEA8vOuwyF5A3gMdRjxmjigW_33hkZ-8-6cVizN8MTtCjgDEWtG3KSElRINFfMDHJbrjKDLO8Gj5EVNgvQo=DzRUe3tAyrhXS6D9OdOiWAYQdvlLaZGzqrOrIY_OgOsu6-54W17PpzAAVG8z3BYUcK3UduF219bPQb8IJjX_0j8Uk0Vj0aJ=5jc3ZA7NWblhGNgA=IIwHDNjC4tWK3Gei94_pmCIxXdPtyl=TE5paEuYVwetKw0OWNhQ2-3qjxUNP0cU99fjE-fEYJuKVkJDQ1McjZg5K9WuCdsZv_2Cs1LoY=1cgwSc_jJ75QCSgiazDIOjF2VL2mVCAt-wxPhyjWB_d8IqHCO3ytem8lpfO6Yg0i3D6LrqAT_DUkRypvoMxpBU7DcmEtN8Ywt5j1mcrLIxuCu5M--gbIvvN_9W2okVpzFiB8yJ4E5gSmCd2jAo3u3yHbpV0DtGYVEWU2s6q7V3akg1-v6F0V7LF2mAhfMA6D2MC35HdQBYDw0Ww9J2l3asQwgfY6q9e6=PIBAtl1P0WY-ysekQRVLr99V0ZS=l9efdoL3CeG8IQjFR5T5I-vFrdm-J-jqRstj8lDH-LhvNsBXOVIScUwNRUDrqx8ZERJ2GaACAScu7PJYBk41iWJGDdftlJ_QPpJTzsVb0hb3ugqg0H=4lDxh_SL2SOeR5_Vfb29JQsA=JLT=u4PQXCzdSQWaRK-i2ZLXEHuI_FtlsHoOhF0SkOJNp=gx5uvE8rNkq5whrxapBYHHNo0N46Te_8W_fvgyuQhdiFT6kT-SeJYpGxZXbpkeVZjEFt9ffFC_lTOvq9f2ICbvY7h04bBEvz=BhhBS4cEI9yVcQHU9mPqvwhJBeG4r8oj6bbPmdJuVHU8xcQel7q5RpO1UZ56cuG1wLC7m7gw9pDtTv-FzzYCZ-f0em11amSQzT=4zHOKS5WTStMFpdZQpDqoLaN0XioZdVAkGZ7I=oRvX0ta2aPb9288ZA8IXK3QJHF_mkIialEllQ4DlkkrZvJyplUizSeZmeq88W3i2sjyuA384Ax=6UbaZbHQsLRzk0s3msD0=3ZBYDOZPt2u66EOgPN6v_c3kHBrhz9CPKDkPcXQtOu8ZW6Je_D_PyoPYpll0zQRg9JSrIAsOTIjW1HIOLYI-RSaNXuacZWRv3Kquh_90JNyw9h_cLp-CuwkqqrMkVZM9jTCCrharrRbBmr8iNJ2quwYGzRvsBEud_=8613aHzCxSZtfHU0X4e46r7d5FEAxdZ711HMSoW9OUR4XdgbbIv==pNKRPb4KBAklV70sNCjczfujyML4F9DPkrglLjO2rQuGOKxMpe8GNNivTIAoZJma3ML9LjFYpT83xRsGSXo6etzX1POdld4ZaRox7eI-Cw9YZQ1CSHG2y0hMbQVWWSXAi-d5mMJtFTM-o7YP3Bt-wpgl17iHJf09=_9G=LMG-mERkMpyv0-zWWjj4zN4UPezomRjhEKfH9q0_hZFCQLhvdWhd9=6SqNzl03xh3h0p85W27FfkKW5Cm9tm7mkBmOeoqL6JQ_xzD1a4JcbkOjEUV-aOXgWg-z_Am4qVC5qvWNPN-sq8MXGjcUeoVrR==ea77avAQ7EvVgvCzvZos8DgIqsVS_ULS1wOsAt0ge_hsdPI0YujjRaMuovIDDQp2wY7-sJwSfVgFtwKw-Y-v0csaaM8Uw36xAQBFY0iB0fgOs0I7W6ueCk5CpeixvXHj5XWuhiSDsaZxb4RG8bTaKraK5jClUI6d6IrR12mPw3yS6BMdr0-5EUf_sDfwP5G_NOz3pP0FkvXP2v_rzYIA2St5MVGYJ7IOGt9brRdo5BLjuyoasWe5DSVT2gK3lHdk6UhtlNgxWdmjFl0ydVxj8jF8LHEXJtkkZONRPcLRmrhtgAl-Xf_FKwFYEpMdbsRBU9ZVt6u3Xo_gd5tA=I_JFeTIgfpxD82KN5JSumCg=Jf3DxtQRlkFwiSrC06JfgtOQe_UUGaRY9lZ3bQdJE5EsZvI_AATCORbJjc==77-oEXERzQTzuSZzD1VdK5FiQTA-6-sR0J1lCZ0Kmsdqt2Smx=ar4mAZVOa1m-rlOdTzVl5iR',
            # 'p8kOmysnbc-z': 'q',
            # 'p8kOmysnbc-d': 'ADaAhIDBCKGBgQGAAYIQgISigaIAwBGAzPpCxg_33ocxnsD_CAD25RIviEUIJgAAAAArd0EfAovjArvgdtBMzYMXJCgRsNo',
            # 'p8kOmysnbc-c': 'AEAtJ-iQAQAAsdjKVw9fkSsmF1C9QjJjIs02jVnfA_wNKHvQD_blEi-IRQgm',
            # 'p8kOmysnbc-b': '-f8k6d2',
            # 'p8kOmysnbc-f': 'A8G3LuiQAQAA79vcKkpe7tz8IOa2kVqBna6ucWr-lXzwobkcTTUQNUnsZY9QAWj5rnuucuopwH9eCOfvosJeCA==',
            **shape_headers,
            'j_username': 'evfregvg@gmail.com',
            'j_password': 'dfhrtfgjhrfyjn',
            'CSRFToken': '31ec52ca-bae8-4e98-a8e3-1190d049903b',
            'pb_tracking_id': '0f9ec63b-e687-4397-98c2-147326860d91',
        }

        response = session.post('https://p-bandai.com/hk/login', headers=headers, data=data, impersonate=impersonate)
        return response
      
    async def main(n):
        return await asyncio.gather(*[
            demo(
                href="https://p-bandai.com/",
                script_url="https://p-bandai.com/_ui/responsive/common/js/common.js?single",
                vmp_regexp=r'"(/_ui/responsive/common/js/common.js\?async&seed=.*?&p8kOmysnbc--z=q)"',
                request={
                    "url": 'https://p-bandai.com/hk/login',
                },
                pkey='p8kOmysnbc',
                verifier=baidai_login,
                # proxy="127.0.0.1:7890"
            ) for _ in range(n)
        ])
        
    for _ in range(1):
        asyncio.run(main(1))
