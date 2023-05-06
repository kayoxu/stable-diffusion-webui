# coding=utf-8
import os
import sys
import time
import json
import http.client
import hashlib
import urllib
import random
from pygtrans import Translate
import translators as ts

from translate.baiduTransKey import *

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def zh2en(data: str):
    # 0 google 1baidu
    typeType = 1

    if data == '' or data.lower().__contains__('@nts'):
        data = data.replace('@NTS', '').replace('@nts', '')
        return data

    if data == '' or data.lower().__contains__('@baidu'):
        data = data.replace('@BAIDU', '').replace('@baidu', '')
        typeType = 1
    elif data == '' or data.lower().__contains__('@google'):
        data = data.replace('@GOOGLE', '').replace('@google', '')
        typeType = 0

    isok = True

    if data != '':

        if typeType == 0:
            data, isok = useGoogle(data, isok)
        elif typeType == 1:
            data, isok = useBaidu(data, isok)

    if isok:
        print('翻译成功了：\n' + data)
    else:
        print('翻译失败了：\n' + data)

    return data


def useGoogle(data, isok):
    try:
        # client = Translate(target='en-US', proxies={'http': 'http://192.168.5.191:1081', 'https': 'http://192.168.5.191:1081'})
        client = Translate(target='en-US', proxies={'socks5': 'http://192.168.5.191:1080'})
        data = client.translate(data).translatedText
    except:
        try:
            print('谷歌翻译失败，使用百度翻译')
            bt = Baidu_trans()
            data = bt.trans(data)['result']['dst']
        except:
            isok = False
            pass
    return data, isok


def useBaidu(data, isok):
    try:
        bt = Baidu_trans()
        data = bt.trans(data)['result']['dst']
    except:
        pass

    return data, isok


"""
官方文档：https://fanyi-api.baidu.com/doc/21
"""


class Baidu_trans(object):
    def __init__(self):
        self.appid = baidu_appid
        self.secret_key = baidu_secret_key
        self.from_lang = 'auto'
        self.to_lang = 'en'

        """
        返回状态码2000为成功
                2001为错误
        """

    def get_url(self, query):
        base_url = '/api/trans/vip/translate'
        salt = random.randint(32768, 65536)
        sign = self.appid + query + str(salt) + self.secret_key
        sign = hashlib.md5(sign.encode()).hexdigest()
        myurl = base_url + '?appid=' + self.appid + '&q=' + urllib.parse.quote(
            query) + '&from=' + self.from_lang + '&to=' + self.to_lang + '&salt=' + str(
            salt) + '&sign=' + sign
        return myurl

    def trans(self, query):
        httpClient = None

        myurl = self.get_url(query)

        try:
            httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
            httpClient.request('GET', myurl)

            response = httpClient.getresponse()
            result_all = response.read().decode("utf-8")
            result = json.loads(result_all)

            data = result.get('trans_result', ['error'])[0]
            error_code = result.get('error_code', '')
            error_msg = result.get('error_msg', '')

            if isinstance(data, dict):
                code = 2000
            else:
                code = 2001
            return {"code": code, "result": data, "error_code": error_code, "error_msg": error_msg}


        except Exception as e:
            print(e)
            return {"code": 2001, "data": {}}

        finally:
            if httpClient:
                httpClient.close()

    def trans_limit(self, query):
        result = self.trans(query)
        time.sleep(1.1)
        return result


#
if __name__ == '__main__':
    trans = Baidu_trans()

    query_list = [
        "Adversaries may execute their own malicious payloads by hijacking the Registry entries used by services.",
        "Mark Russinovich. (2019, June 28). Autoruns for Windows v13.96. Retrieved March 13, 2020.",
        "Service changes are reflected in the Registry.",
        "Modification to existing services should not occur frequently.",
        "Adversaries may create or modify Windows services to repeatedly execute malicious payloads as part of persistence.",
        "Monitor processes and command-line arguments for actions that could create or modify services."
    ]

    for query in query_list:
        res = trans.trans_limit(query)
        if res.get("code") == 2000:
            print(res["result"]["dst"])
        else:
            print("code:{}".format(res["code"]))
