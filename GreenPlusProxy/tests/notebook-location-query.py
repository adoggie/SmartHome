
import pymongo
from bson import ObjectId
import pandas as pd
import numpy as np

"""
查询设备历史定位轨迹
"""
conn = pymongo.MongoClient('localhost',27017)
# print conn.database_names()
db = conn['BlueEarth']
# print db.collection_names()
coll = db['Device']
rs = coll.find()
# print list(rs)
# print coll.find_one({'_id':ObjectId('5ba34f5df12a35e13a39fcd5')})
rs = db['Position'].find({'device_type':'ev25'}).sort('report_time',-1)
rs = list(rs)
df = pd.DataFrame(rs)
fields = ['device_id','device_type','lat','lon','address','report_time','ymdhms']
df = df[fields]

df