#coding:utf-8

import pymongo
# from bson import ObjectId
# import pandas as pd
# import numpy as np

"""
创建索引脚本
"""
conn = pymongo.MongoClient('localhost',27017)
db = conn['BlueEarth']
coll = db['Position']
coll.create_index([ ('device_id', pymongo.ASCENDING),('timestamp', pymongo.ASCENDING) ] )


