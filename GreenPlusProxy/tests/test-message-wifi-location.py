import pymongo
from bson import ObjectId
import json

"""
创建索引脚本
"""
conn = pymongo.MongoClient('localhost',27017)
db = conn['BlueEarth']
coll = db['Position']

db = conn['blue_earth_device_log']
coll = db['868120191087078']
wifis =  list(coll.find({'name':'MessageWifiExtension'}).sort('timestamp',-1).limit(5))

data=[]
for wifi in wifis:
    data.append(wifis[0]['wifi_data'])
print json.dumps(data)

wifi_data_str="""
[{"signal": 80, "mac": "1d:93:3b:d7:1c:2a"}, {"signal": 220, "mac": "ef:09:ac:95:32:40"}, {"signal": 20, "mac": "75:90:97:32:2a:47"}, {"signal": 100, "mac": "09:80:79:4f:72:4c"}, {"signal": 152, "mac": "bc:57:73:b5:00:5f"}]
[[{"signal": 80, "mac": "1d:93:3b:d7:1c:2a"}, {"signal": 220, "mac": "ef:09:ac:95:32:40"}, {"signal": 20, "mac": "75:90:97:32:2a:47"}, {"signal": 100, "mac": "09:80:79:4f:72:4c"}, {"signal": 152, "mac": "bc:57:73:b5:00:5f"}], [{"signal": 80, "mac": "1d:93:3b:d7:1c:2a"}, {"signal": 220, "mac": "ef:09:ac:95:32:40"}, {"signal": 20, "mac": "75:90:97:32:2a:47"}, {"signal": 100, "mac": "09:80:79:4f:72:4c"}, {"signal": 152, "mac": "bc:57:73:b5:00:5f"}], [{"signal": 80, "mac": "1d:93:3b:d7:1c:2a"}, {"signal": 220, "mac": "ef:09:ac:95:32:40"}, {"signal": 20, "mac": "75:90:97:32:2a:47"}, {"signal": 100, "mac": "09:80:79:4f:72:4c"}, {"signal": 152, "mac": "bc:57:73:b5:00:5f"}], [{"signal": 80, "mac": "1d:93:3b:d7:1c:2a"}, {"signal": 220, "mac": "ef:09:ac:95:32:40"}, {"signal": 20, "mac": "75:90:97:32:2a:47"}, {"signal": 100, "mac": "09:80:79:4f:72:4c"}, {"signal": 152, "mac": "bc:57:73:b5:00:5f"}], [{"signal": 80, "mac": "1d:93:3b:d7:1c:2a"}, {"signal": 220, "mac": "ef:09:ac:95:32:40"}, {"signal": 20, "mac": "75:90:97:32:2a:47"}, {"signal": 100, "mac": "09:80:79:4f:72:4c"}, {"signal": 152, "mac": "bc:57:73:b5:00:5f"}]]
"""


def wifi_test():
    from mantis.BlueEarth.tools.lbs import gd_convert_wifi_location
    import traceback

    ak = '0b7d114fdc4eb50079408292b7249015'
    imei = '868120191087078'
    # bts = (pos.mcc,pos.mnc,pos.lac,pos.cell_id,pos.signal)
    wifi_data = json.loads(wifi_data_str)[0]
    macs = map(lambda wifi: (wifi['mac'], wifi['signal']), message.wifi_data)
    try:
        data = gd_convert_wifi_location(ak, imei, macs, debug=instance.getLogger().debug)

