# coding: utf-8

from mantis.fundamental.nosql.mongo import Connection
from mantis.BlueEarth import model
import csv

db = Connection('constant_reference').db
coll = db['lbs_cell']
# 初始化 lbs 基站数据库
csvfile = open('/tmp/cell.csv','rb')
reader = csv.reader(csvfile)
for row in reader:
    mcc, mnc, lac, cell, lat, lon, addr = row
    data = dict(mcc = int(mcc), mnc=int(mnc),lac=int(lac),cell=int(cell),
                lat=float(lac),lon=float(lon),addr = addr)
    coll.insert_one(data)


