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
产品信息
"""

# @login_check
def get_product_list():
    """
    查询商品列表
    """ 
    # user = g.user
    products = model.Product.find()
    main = instance.serviceManager.get('main')
    static_url = main.getConfig().get('static_root_url')

    result = []
    for prd in products:
        prd.url = static_url+'/'+prd.url
        prd.image_url = static_url+'/'+prd.image_url
        prd.slide_image_url = static_url+'/'+prd.slide_image_url
        data = prd.dict()
        result.append(data)
    return CR(result=result).response

# @login_check
def get_product():
    """
    """
    # user = g.user
    sku = request.values.get('sku')

    product = model.Product.get(sku=sku)
    if not product:
        return ErrorReturn(ErrorDefs.ObjectNotExist,u'产品对象不存在').response

    main = instance.serviceManager.get('main')
    static_url = main.getConfig().get('static_root_url')

    product.url = static_url + '/' + product.url
    product.image_url = static_url + '/' + product.image_url
    product.slide_image_url = static_url + '/' + product.slide_image_url

    data = product.dict()
    images = product.content.split(',')
    data['content_urls'] = []
    for image in images:
        url = static_url+'/product/'+product.sku+'/'+image
        data['content_urls'].append(url)
    return CR(result=data).response

