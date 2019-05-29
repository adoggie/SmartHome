# coding: utf-8

import json
from mantis.fundamental.nosql.mongo import Connection
from mantis.fanbei.smarthome import model
from mantis.fundamental.parser.yamlparser import YamlConfigParser
from mantis.fundamental.utils.timeutils import timestamp_current
from mantis.fundamental.utils.useful import object_assign

def get_database():
    db = Connection('SmartHome').db
    return db
model.set_database(get_database())

def init_database():
    data = YamlConfigParser('./init-data.yaml').props

    get_database().HomeProject.remove()
    _ = model.HomeProject.get_or_new()
    _.assign( data.get('project'))
    _.save()

    get_database().HomeGarden.remove()
    for r in data.get('garden_list'):
        _ = model.HomeGarden.get_or_new()
        _.assign(r)
        _.save()

    get_database().Building.remove()
    for r in data.get('building_list'):
        _ = model.Building()
        _.assign(r)
        _.save()

    get_database().RoomTemplate.remove()
    for r in data.get('room_template_list'):
        f = open( r['profile'])
        content = f.read()
        r['profile'] = content
        _ = model.RoomTemplate()
        _.assign(r)
        _.save()

    get_database().RoomArea.remove()
    for r in data.get('room_area_list'):
        _ = model.RoomArea()
        _.assign(r)
        _.save()

    get_database().DeviceServer.remove()
    for r in data.get('device_server_list'):
        _ = model.DeviceServer()
        _.assign(r)
        _.save()

    get_database().SmartDevice.remove()
    for r in data.get('smartbox_list'):
        _ = model.SmartDevice()
        _.assign(r)
        _.save()

    get_database().Sensor.remove()
    for r in data.get('sensor_list'):
        _ = model.Sensor()
        _.assign(r)
        _.save()



init_database()

print 'database initialized.'

