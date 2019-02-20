#coding: utf-8
"""
路径轨迹抽吸、过滤处理

考虑 采用高德的抓路服务或者百度鹰眼服务进行绑路服务

"""
from math import sin, cos, sqrt, atan2, radians
from functools import partial

def distance(coord1, coord2):
	R = 6373.0
	lat1 = radians(coord1[0])
	lon1 = radians(coord1[1])
	lat2 = radians(coord2[0])
	lon2 = radians(coord2[1])

	dlon = lon2 - lon1
	dlat = lat2 - lat1
	a = (sin(dlat/2))**2 + cos(lat1) * cos(lat2) * (sin(dlon/2))**2
	c = 2 * atan2(sqrt(a), sqrt(1-a))
	distance = R * c
	return distance

from mantis.BlueEarth.types import PositionSource

def get_distance(p1,p2):
    return distance( (p1['lat'],p1['lon']),(p2['lat'],p2['lon']) ) * 1000


MAX_LBS_DISTANCE = 600

def find_LL(n,rs):
    start = -1
    end  = -1
    while n< len(rs):
        p = rs[n]
        if p['position_source'] == PositionSource.LBS :
            if start == -1:
                start = n
            end = n
        else:
            if start != -1:
                break
            # print 'GPS'
        n = n + 1
    return start,end

def clean_path(positions):
    """
    1. G,L,G  消除L
    2. G,L1,L,,G  如果L2-L1 > 400 , 保留L1,L2
    3. G,L1,L2,L3,.. 仅仅记录G,L1

    删除重复的坐标
    """
    positions = clear_duplicated_coordinates(init_data(positions))

    rs = positions
    n = 0
    friends = []
    while n< len(rs):
        start,end = find_LL(n,rs)
        if start == -1:
            break
        ll_num = end - start + 1
        if ll_num >= 1 :
            while start <= end-1:

                p1 = rs[start]
                p2 = rs[start+1]
                # friends.append((p1, p2))
                dist = get_distance(p1,p2)
                if dist < MAX_LBS_DISTANCE:
                    p2['dirty'] = True
                start = start + 1
        n = end + 1

    # for n in range(len(friends)):
    #     p1 ,p2 = friends[n]
    #     dist = get_distance(p1,p2)
    #     if dist < MAX_LBS_DISTANCE:
    #         p2['dirty'] = True

    rs = filter(lambda p:p['dirty'] == False and p['speed']!=0,positions)
    return rs

def init_data(positions):
    for p in positions:
        p['dirty'] = False
        if p['position_source'] == PositionSource.LBS:
            p['speed'] = 1
    return positions


def clear_duplicated_coordinates(positions):
    last = None
    result = []
    for r in positions:
        # del r['_id']
        lon = r['lon']
        lat = r['lat']
        if  last:
            if last['lon'] == lon and last['lat'] == lat:
                print 'skipped..'
                last.update(r)
                continue

        #gps->lbs 计算者距离大于500米属于合法
        # if last['position_source'] == 1 and r['position_source'] == 2:
        #     r['speed'] = 999

        last = r

        # if last['speed'] == 0 : #and r['position_source']==1:
        #     continue
        # last['lon'], last['lat'] = wgs84_to_gcj02(lon, lat)
        result.append(last)
    return result