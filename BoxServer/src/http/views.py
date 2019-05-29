#coding:utf-8

import json
from flask import Flask,send_file
from flask import Response

from flask import render_template
from mantis.fundamental.application.app import  instance
from mantis.fundamental.flask.utils import nocache

@nocache
def index():
    # profiles = get_strategy_running_profile()
    # return Response(json.dumps(profiles),content_type='application/json')
    # return render_template('index.html',profiles = profiles)
    return render_template('index.html')
