# -*- coding: utf-8 -*-
import os
import json
from flask import render_template
from flask import request
from flask_login import login_required
from docker import Client

from app import app
from app import db
from app import socketio
from app.models import ProjectModel
from app.models import ServerModel
from app.models import AppModel

REGISTRY_IP = '172.16.6.130:5000/'
APPS = None
APP_NAME = None
HOST = None
IMAGE = None
PORT = None


@app.route('/apps')
@login_required
def apps():
    page = request.args.get('page', 1, type=int)
    pagination = AppModel.query.order_by(
        AppModel.create_on.desc()).paginate(
            page, app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)
    apps = pagination.items
    return render_template('container.html', apps=apps, pagination=pagination)


@app.route('/apps/create/<verify>')
@login_required
def create_app(verify):
    project = ProjectModel.query.filter_by(verify=verify).first()
    servers = ServerModel.query.order_by(ServerModel.create_on.desc())
    app_verify = ''.join(map(lambda xx: (hex(ord(xx))[2:]), os.urandom(16)))
    return render_template(
        'create-app.html',
        project=project,
        servers=servers,
        app_verify=app_verify
    )


@app.route('/apps/per/<verify>', methods=['GET', 'POST'])
def per_app(verify):
    apps = AppModel.query.filter_by(verify=verify).first()
    global APPS
    global APP_NAME
    global HOST
    global IMAGE
    global PORT
    if request.method == 'POST' and apps is None:
        APP_NAME = appname = request.form['appname']
        HOST = ip = request.form['server']
        PORT = port = request.form['port']
        IMAGE = image = REGISTRY_IP + request.form['image']
        APPS = apps = AppModel(
            appname=appname,
            port=port,
            host=ip,
            image=image,
            verify=verify,
        )
        db.session.add(apps)
        db.session.commit()
        return render_template('app.html', apps=apps)
    elif apps is not None:
        APPS = apps
        APP_NAME = apps.appname
        HOST = apps.host
        IMAGE = apps.image
        PORT = apps.port
    elif apps is None:
        apps = APPS
    return render_template('app.html', apps=apps)


@app.route('/apps/create', methods=['POST'])
def create_app_socket():
    logs = []
    status = json.loads(container_status())['status']
    # 如果容器还没有,就开始创建
    if status == 'pending':
        cli = Client(base_url=HOST+':5678')
        for line in cli.pull(IMAGE, stream=True):
            socketio.emit('response', json.dumps({'resp': line}))
            logs.append(line)
        container = cli.create_container(
            image=IMAGE, ports=[PORT], name=APP_NAME,
            host_config=cli.create_host_config(port_bindings={
                3000: (HOST, PORT)
            })
        )
        APPS.containerId = container.get('Id')
        db.session.add(APPS)
        db.session.commit()
        response = cli.start(container=container.get('Id'))
        if response is not None:
            return json.dumps({'msg': 'false'})
    return json.dumps({'msg': 'ok'})


@app.route('/apps/per/status', methods=['POST'])
def container_status():
    status = find_container(APP_NAME, HOST)
    return json.dumps({'status': status})


@app.route('/apps/all/status', methods=['POST'])
def all_container_status():
    resp = {}
    data = json.loads(request.get_data())
    for i in range(len(data['data'])):
        apps = AppModel.query.filter_by(appname=data['data'][str(i)]).first()
        resp[str(i)] = find_container(apps.appname, apps.host)
    return json.dumps(resp)


def find_container(appName, host):
    run_names = []
    all_names = []
    cli = Client(base_url=str(host)+':5678')
    run_containers = cli.containers()
    all_containers = cli.containers(all=True)
    for container in run_containers:
        run_names.append(container['Names'][0].split('/')[1])
    for container in all_containers:
        all_names.append(container['Names'][0].split('/')[1])
    if appName in run_names:
        status = 'up'
        return status
    else:
        if appName in all_names:
            status = 'down'
            return status
        else:
            status = 'pending'
            return status


@app.route('/apps/check/appname', methods=['POST'])
def check_appname():
    data = json.loads(request.get_data())
    app = AppModel.query.filter_by(appname=data['data']).first()
    if app is None:
        return json.dumps({'resp': 'ok'})
    else:
        return json.dumps({'resp': 'no'})


@app.route('/apps/delete', methods=['POST'])
def delete_app():
    data = json.loads(request.get_data())
    apps = AppModel.query.filter_by(appname=data['data']).first()
    cli = Client(base_url=apps.host+':5678')
    response = cli.remove_container(container=apps.containerId, force=True)
    if response is None:
        try:
            db.session.delete(apps)
        except:
            db.session.roolback()
            return json.dumps({'resp': 'no'})
        db.session.commit()
        return json.dumps({'resp': 'ok'})
    else:
        return json.dumps({'resp': 'no'})


@socketio.on('start app')
def start_app(message):
    appName = message['appName']
    apps = AppModel.query.filter_by(appname=appName).first()
    cli = Client(base_url=apps.host+':5678')
    response = cli.start(container=apps.containerId)
    socketio.emit('status response', {'data': response, 'info': '运行中', 'color': '#169f2d'})


@socketio.on('stop app')
def stop_app(message):
    appName = message['appName']
    apps = AppModel.query.filter_by(appname=appName).first()
    cli = Client(base_url=apps.host+':5678')
    response = cli.stop(container=apps.containerId)
    socketio.emit('status response', {'data': response, 'info': '待机', 'color': 'red'})


# 获取应用的运行日志
@app.route('/apps/logs', methods=['POST'])
@login_required
def get_app_logs():
    data = json.loads(request.get_data())
    cli = Client(base_url=str(data['host'])+':5678')
    for log in cli.logs(container=data['appName'], stream=True):
        socketio.emit('logs response', {'data': log})
