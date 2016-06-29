# -*- coding: utf-8 -*-
import os
import json
import subprocess
import time
from flask_login import login_required, current_user
from flask import render_template, request
from docker import Client
from io import BytesIO

from app import app, redis, db, socketio
from app.models import ProjectModel

false = False
null = None
true = True

SUCCESS = 1
FALSE = 2


@app.route('/build')
@login_required
def build_code():
    page = request.args.get('page', 1, type=int)
    pagination = ProjectModel.query.order_by(
        ProjectModel.create_on.desc()).paginate(
        page, app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)
    projects = pagination.items
    return render_template(
        'build.html', projects=projects, pagination=pagination)


@app.route('/build/new')
@login_required
def build_code_new():
    org_repos = {}
    # github 中的个人数据
    github_data = redis.hget(current_user.id, 'github_data')
    if github_data is not None:
        github_data = json.loads(github_data)
    # github个人的组织信息
    github_orgs_data = redis.hget(current_user.id, 'github_orgs_data')
    if github_orgs_data is not None:
        github_orgs_data = eval(github_orgs_data)
    # 个人拥有的项目信息
    github_user_repos = redis.hget(current_user.id, 'github_user_repos')
    if github_user_repos is not None:
        github_user_repos = eval(github_user_repos)
    # 组织拥有的项目信息
    if github_orgs_data is not None:
        for github_org_data in github_orgs_data:
            repo = eval(redis.hget(
                current_user.id, github_org_data['login']
            ))
            org_repos[github_org_data['login']] = repo

    '''以下是gitlab数据'''
    # gitlab 个人数据
    gitlab_data = redis.hget(current_user.id, 'gitlab_data')
    if gitlab_data is not None:
        gitlab_data = json.loads(gitlab_data)
    # gitlab 个人项目
    gitlab_user_repos = redis.hget(current_user.id, 'gitlab_user_repos')
    if gitlab_user_repos is not None:
        gitlab_user_repos = eval(gitlab_user_repos)

    return render_template(
        'build-new.html',
        github_data=github_data,
        github_orgs_data=github_orgs_data,
        github_user_repos=github_user_repos,
        github_org_repos=org_repos,

        gitlab_data=gitlab_data,
        gitlab_user_repos=gitlab_user_repos
    )


@app.route('/create_project', methods=['POST'])
@login_required
def create_project():
    data = json.loads(request.get_data())
    code = str(data['code']).rstrip()
    proName = str(data['proName'])
    verify = ''.join(map(lambda xx: (hex(ord(xx))[2:]), os.urandom(16)))
    code_address = redis.hget(current_user.id, code)
    application = ProjectModel.query.filter_by(proname=proName).first()
    if application is not None:
        return json.dumps({'msg': '应用名字重复'})
    else:
        project = ProjectModel(
            proname=proName,
            address=code_address,
            verify=verify
        )
        db.session.add(project)
        db.session.commit()
        c1 = subprocess.Popen(
            'git clone ' + code_address,
            cwd=app.config['CODE_FOLDER'], shell=True)
        subprocess.Popen.wait(c1)
        return json.dumps({'msg': 'ok', 'verify': project.verify})


@app.route('/build/new/<verify>')
def per_project(verify):
    project = ProjectModel.query.filter_by(verify=verify).first()
    return render_template('project.html', project=project)


@socketio.on('build project')
def get_log(json):
    logs = []
    project = ProjectModel.query.filter_by(proname=json['data']).first()
    if not project.is_build():
        os.chdir(app.config['CODE_FOLDER'] + '/' + json['data'])
        cli = Client(base_url='123.206.205.95:5678')
        lines = cli.build(path=os.getcwd(), stream=True, decode=True,
                          tag=str(json['data']))
        for line in lines:
            logs.append(line)
        redis.hset(project.id, project.verify, logs)
        send_log(logs)
        project.build = True
        if 'Successfully built' in logs[-1]['stream']:
            project.success = 1
        else:
            project.success = 2
        db.session.add(project)
        db.session.commit()
    else:
        lines = eval(redis.hget(project.id, project.verify))
        send_log(lines)


def send_log(lines):
    for line in lines:
        if 'stream' in line:
            socketio.emit('response', {'resp': line})
        elif 'errorDetail' in line:
            socketio.emit(
                'response', {
                    'resp': line['errorDetail']
                }
            )
        elif 'status' in line:
            socketio.emit('response', {'resp': line})


@app.route('/get/build_status', methods=['POST'])
def get_build_status():
    if request.method == 'POST':
        verify = json.loads(request.get_data())['data']
        project = ProjectModel.query.filter_by(verify=verify).first()
        return json.dumps({'status': project.success})
