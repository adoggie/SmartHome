# coding: utf-8

from mantis.fundamental.nosql.mongo import Connection
from mantis.BlueEarth import model


def get_database():
    db = Connection('BlueEarth').db
    return db

model.get_database = get_database

def init_test_device():
    device = model.Device.create(device_id='868120201788186',device_type='gt03',name= u'老公的车').save()
    device = model.Device.create(device_id='868120205647263',device_type='ev25',name= u'张师傅').save()
    device = model.Device.create(device_id='868120191087078',device_type='gt310',name= u'Eric.son').save()

device = model.Device.create(device_id='868120200177639',device_type='gt03',name= u'设备1').save()



