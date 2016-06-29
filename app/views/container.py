# -*- coding: utf-8 -*-
import os
import json
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash
from flask_login import login_required
from docker import Client

from app import app
from app import db
from app.models import ProjectModel
from app.models import ServerModel
from app.models import AppModel


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
    if request.method == 'POST' and apps is None:
        appname = request.form['appname']
        ip = request.form['server']
        port = request.form['port']
        image = request.form['image']

        try:
            cli = Client(base_url=ip+':5678')
            container = cli.create_container(
                image=image, ports=[port], name=appname,
                host_config=cli.create_host_config(port_bindings={
                    3000: (ip, port)
                })
            )
            apps = AppModel(
                appname=appname,
                port=port,
                host=ip,
                image=image,
                verify=verify,
                containerId=container.get('Id')
            )
            db.session.add(apps)
            db.session.commit()

            response = cli.start(container=container.get('Id'))
            if response is None:
                return redirect(url_for('per_app', verify=verify))
        except:
            flash(u'未知错误', category='danger')
            return redirect(url_for('apps'))
    return render_template('app.html', apps=apps)


@app.route('/apps/per/status', methods=['POST'])
def container_status():
    names = []
    data = json.loads(request.get_data())
    cli = Client(base_url=data['host']+':5678')
    containers = cli.containers()
    for container in containers:
        names.append(container['Names'][0].split('/')[1])
    if data['name'] in names:
        status = 'up'
    else:
        status = 'down'
    return json.dumps({'status': status})


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
    app = AppModel.query.filter_by(appname=data['data']).first()
    try:
        db.session.delete(app)
    except:
        db.session.roolback()
        return json.dumps({'resp': 'no'})
    db.session.commit()
    return json.dumps({'resp': 'ok'})
