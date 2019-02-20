#coding:utf-8
import json
import pymongo
from flask import Flask,request,g
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

from mantis.fundamental.application.app import instance
from mantis.fundamental.flask.webapi import ErrorReturn,CR
from mantis.fundamental.utils.timeutils import timestamp_current,datetime_to_timestamp,timestamp_to_str
from mantis.BlueEarth import model

from mantis.BlueEarth.errors import ErrorDefs
from bson import ObjectId
from token import login_check,AuthToken

"""
用户收藏夹
"""

def make_product_url(product):
    main = instance.serviceManager.get('main')
    static_url = main.getConfig().get('static_root_url')

    product['url'] = static_url + '/' + product['url']
    product['image_url'] = static_url + '/' + product['image_url']
    product['slide_image_url'] = static_url + '/' + product['slide_image_url']

def create_favorite():
    """
     收藏产品
    """
    user = g.user
    sku = request.values.get('sku')
    comment = request.values.get('comment','')
    product = model.Product.get(sku=sku)
    if not product:
        return ErrorReturn(ErrorDefs.ObjectNotExist,u'产品不存在').response
    favorite = model.Favorite()
    favorite.user_id = user.id
    favorite.sku = sku
    favorite.number = 1
    favorite.create_time = timestamp_current()
    favorite.order = timestamp_current()
    favorite.comment = comment
    favorite.save()
    return CR(result=favorite.id).response


def get_favorite_list():
    """
    查询收藏商品
    """


    user = g.user
    favorite_list = model.Favorite.collection().find({'user_id':user.id}).sort('order',pymongo.DESCENDING)
    result = []
    for favorite in list(favorite_list):
        data = favorite
        product = model.Product.get(sku=favorite.get('sku'))
        if product:
            data['product'] = product.dict()
            make_product_url(data['product'])

        data['id'] = str(data['_id'])
        del data['_id']
        result.append(data)
    return CR(result=result).response


def get_favorite():
    """
    """
    main = instance.serviceManager.get('main')
    static_url = main.getConfig().get('static_root_url')

    user = g.user
    id = request.values.get('id')
    favorite = model.Favorite.get(user_id=user.id,_id=ObjectId(id))
    if not favorite:
        return ErrorReturn(ErrorDefs.ObjectNotExist,u'对象不存在').response
    result = favorite.dict()
    product = model.Product.get(sku=favorite.sku)
    if product:
        result['product'] = product.dict()
        make_product_url(result['product'])
    return CR(result=result).response


def remove_favorite():
    """
    """
    user = g.user
    id = request.values.get('id')
    favorite = model.Favorite.get(_id = ObjectId(id))
    if not favorite:
        return ErrorReturn(ErrorDefs.ObjectNotExist,u'对象不存在').response
    favorite.delete()
    return CR().response