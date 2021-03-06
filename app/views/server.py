# -*- coding: utf-8 -*-
import os
from flask import \
    (
        render_template,
        request,
        flash,
        redirect,
        url_for,
        json,
        jsonify
    )
from flask_socketio import emit
from flask_login import login_required
from docker import Client

from app import app, socketio, db
from app.forms import ServerForm
from app.models import ServerModel


IP_LISTS = []


class ServerService(object):
    @staticmethod
    def get_server_by_nickname(nickname):
        return ServerModel.query.filter_by(nickname=nickname).first()

    @staticmethod
    def get_server_by_ip(ip):
        return ServerModel.query.filter_by(Ip=ip).first()

    @staticmethod
    def get_servers(page):
        return ServerModel.query.order_by(
            ServerModel.create_on.desc()).paginate(
            page, app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)


@app.route('/server', methods=['GET', 'POST'])
@login_required
def add_server():
    form = ServerForm()
    if request.method == 'POST' and form.validate_on_submit:
        nickname = form.nickname.data
        ip = form.ip.data
        if ServerService.get_server_by_nickname(nickname) is not None:
            flash(u'添加失败,名称已被占用', 'danger')
            redirect(url_for('add_server'))
        elif ServerService.get_server_by_ip(ip) is not None:
            flash(u'添加失败,该主机IP已被添加', 'danger')
            redirect(url_for('add_server'))
        else:
            server = ServerModel(nickname=nickname, Ip=ip)
            db.session.add(server)
            db.session.commit()
            flash(u'添加成功', 'success')
    page = request.args.get('page', 1, type=int)
    pagination = ServerService.get_servers(page)
    servers = pagination.items
    return render_template('server.html',
                           form=form, servers=servers, pagination=pagination)


@app.route('/server/ping', methods=['POST'])
@login_required
def ping_server():
    if request.method == 'POST':
        rsp = {}
        ip = json.loads(request.get_data())
        for i in range(len(ip['data'])):
            resp_num = check_ping(ip['data'][str(i)])
            rsp[str(i)] = resp_num
            if resp_num == 0:
                if not check_docker(ip['data'][str(i)]):
                    rsp[str(i)] = 'false'
        return json.dumps(rsp)


def check_ping(ip):
    return os.system('ping -c 1 -W 1 ' + ip)


def check_docker(ip):
    client = Client(base_url=ip+':5678')
    try:
        client.info()
        return True
    except Exception, e:
        return False


@app.route('/server/delete', methods=['POST'])
@login_required
def delete_server():
    data = json.loads(request.get_data())
    host = data['data']
    server = ServerModel.query.filter_by(Ip=host).first()
    if server is None:
        return json.dumps({'resp': 'no'})
    else:
        db.session.delete(server)
        db.session.commit()
        return json.dumps({'resp': 'ok'})
