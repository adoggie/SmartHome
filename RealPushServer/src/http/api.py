#coding:utf-8

import json
from flask import Flask,request
from flask import Response

from flask import render_template
from mantis.fundamental.application.app import  instance
from mantis.fundamental.flask.webapi import *
from mantis.fundamental.flask.utils import nocache
from mantis.fanbei.smarthome import model
from mantis.fanbei.smarthome.message import *
from mantis.fanbei.smarthome.errors import *

def get_active_devices():
    pass