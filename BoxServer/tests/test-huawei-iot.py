#coding:Utf-8

"""
测试下发iot的控制命令到 agent-lite 设备

"""

import json,os,os.path,time,datetime,traceback
import requests
import urllib
import urllib2
import ssl
# import requests.packages.urllib3.util.ssl_
# requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL'


ssl._create_default_https_context = ssl._create_unverified_context

def get_iot_app_access_token():
    """
    refs :
        https://support.huaweicloud.com/api-IoT/iot_06_0007.html
    :return:
    """
    url = "https://117.78.47.187:8743/iocm/app/sec/v1.1.0/login"
    data =dict( appId = "yU4yKoAFF_qgUG9xEONDa34Hpe4a", secret = "Dv3ybH9znMwSfH9i1cs9qBrse80a")
    res = requests.post(url,data)
    data = res.json()
    print data

def test_command_iot_send():
    requests.DEFAULT_RETRIES = 5
    # requests.adapters.DEFAULT_RETRIES = 5
    s = requests.session()
    s.keep_alive = False

    url ="https://117.78.47.187:8743/iocm/app/signaltrans/v1.1.0/devices/{deviceId}/services/{serviceId}/sendCommand?appId={appId}"
    device_id = "2afdb4fe-9af9-4bd8-adb8-f26502386150"
    appId = "yU4yKoAFF_qgUG9xEONDa34Hpe4a"
    service_id = "Light"
    url = url.format(deviceId = device_id,serviceId = service_id , appId = appId)
    headers = {'Content-Type':'application/json' , 'app_key':appId , 'Authorization': 'Bearer{}'.format("a657991dbed881bf34e5297972e27e") }
    data = dict( header= dict(mode='NOACK',method='Switch'), body = dict( value=1)  )
    # url = "https://www.baidu.com/"
    # res = requests.post(url,json = data,headers = headers ,verify=False)
    data = json.dumps(data)
    req = urllib2.Request(url, data, headers)
    res = urllib2.urlopen(req)
    text = res.read()

    print text

if __name__ == '__main__':
    test_command_iot_send()