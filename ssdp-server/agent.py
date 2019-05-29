#coding:utf-8
import web
import json
import traceback

import rokid

"""
https://developer.rokid.com/docs/rokid-homebase-docs/connect/http-remote-driver.html

"""
urls = (
    '/', 'index',
    '/list','DeviceList',
    '/execute','Execute',
    '/command','Command'
)


class DeviceList(object):
    def POST(self):

        data = web.data()

        # print data
        web.header('content-type', 'application/json')

        device_list = rokid.get_device_list()
        jsondata = json.dumps( {"status":0 ,"data": device_list} )
        # jsondata = json.dumps(device_list.device_list)
        return jsondata

"""
https://developer.rokid.com/docs/rokid-homebase-docs/connect/http-remote-driver.html
"""

class Execute(object):
    def POST(self):
        data = web.data()
        print data
        jsondata = json.loads(data)
        try:
            rokid.translate_and_send_command( jsondata )
        except:
            traceback.print_exc()

        resp = {"status": 0,"data": {} }
        web.header('content-type', 'application/json')
        return json.dumps(resp)


if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
