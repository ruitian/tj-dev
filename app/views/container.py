# -*- coding: utf-8 -*-
import os
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
    return render_template('container.html')


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
                    port: 3000
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
            return redirect(url_for('per_app', verify=verify))
    return render_template('app.html', apps=apps)
