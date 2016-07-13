# -*- coding: utf-8 -*-
import os
import json
import subprocess
from flask_login import login_required, current_user
from flask import render_template, request
from docker import Client

from app import app, redis, db, socketio
from app.models import ProjectModel

false = False
null = None
true = True

SUCCESS = 1
FALSE = 2
HOST = app.config['HOST']
REGISTRY = app.config['REGISTRY']


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
        if os.path.exists(app.config['CODE_FOLDER']+'/'+proName):
            # 更新代码
            c2 = subprocess.Popen(
                'git pull origin master',
                cwd=app.config['CODE_FOLDER']+'/'+proName, shell=True)
            subprocess.Popen.wait(c2)
        else:
            # 首次克隆代码
            c1 = subprocess.Popen(
                'git clone ' + code_address,
                cwd=app.config['CODE_FOLDER'], shell=True)
            subprocess.Popen.wait(c1)
        return json.dumps({'msg': 'ok', 'verify': project.verify})


# 手动更新镜像
@socketio.on('update project')
def update_project(message):
    # 更新代码
    c = subprocess.Popen(
        'git pull origin master',
        cwd=app.config['CODE_FOLDER']+'/'+message['data'], shell=True)
    subprocess.Popen.wait(c)
    cli = Client(base_url=HOST)
    response = cli.tag(
        image=REGISTRY+message['data'],
        repository=REGISTRY+message['data'],
        tag=1.0,
        force=True
    )
    if response:
        cli.remove_image(image=REGISTRY+message['data'])
        project = ProjectModel.query.filter_by(proname=message['data']).first()
        project.build = False
        project.success = False
        db.session.add(project)
        db.session.commit()
    socketio.emit('update response', {'data': 'ok'})
    return json.dumps({'resp': 'ok'})


@app.route('/build/new/<verify>')
def per_project(verify):
    project = ProjectModel.query.filter_by(verify=verify).first()
    return render_template('project.html', project=project)


@app.route('/build/project', methods=['POST'])
def get_log():
    logs = []
    json_data = json.loads(request.get_data())
    project = ProjectModel.query.filter_by(proname=json_data['data']).first()
    if not project.is_build():
        os.chdir(app.config['CODE_FOLDER'] + '/' + json_data['data'])
        cli = Client(base_url=HOST)
        for line in cli.build(path=os.getcwd(), stream=True, decode=True,
                              tag=str(REGISTRY + json_data['data'])):
            send_log(line)
            logs.append(line)
        # 向私有仓库推送镜像, 没有log的打印
        for line in cli.push(REGISTRY + json_data['data'], stream=True):
            # 打印出上传的log
            print line
            assert line
        redis.hset(project.id, project.verify, logs)
        project.build = True
        if 'Successfully built' in logs[-1]['stream']:
            project.success = 1
        else:
            project.success = 2
        db.session.add(project)
        db.session.commit()
    else:
        lines = eval(redis.hget(project.id, project.verify))
        for line in lines:
            send_log(line)
    return json.dumps({'msg': 'ok'})


def send_log(line):
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


@app.route('/project/delete', methods=['POST'])
@login_required
def delete_project():
    data = json.loads(request.get_data())
    project = ProjectModel.query.filter_by(proname=data['data']).first()
    cli = Client(base_url=HOST)
    response = cli.remove_image(image=REGISTRY+project.proname, force=True)
    if response is None:
        try:
            db.session.delete(project)
        except:
            db.session.roolback()
            return json.dumps({'resp': 'no'})
        db.session.commit()
        return json.dumps({'resp': 'ok'})
    else:
        return json.dumps({'resp': 'no'})


# 获取镜像的版本
@app.route('/project/version', methods=['POST'])
def get_project_version():
    data = json.loads(request.get_data())
    tags = []
    cli = Client(base_url=HOST)
    images = cli.images()
    for image in images:
        for i in image['RepoTags']:
            if REGISTRY+data['data']+':1.0' == str(i) \
                    or REGISTRY+data['data']+':latest' == str(i):
                tags.append(str(i).split(':')[2])
    return json.dumps({'tags': tags})


# 切换版本
@socketio.on('checkout tag')
def checkout_tag(message):
    project = ProjectModel.query.filter_by(proname=message['proName']).first()
    cli = Client(base_url=HOST)
    if project.tag != message['tagName']:
        resp_1 = tag_image(cli, project.proname, ':latest', '2.0')
        if resp_1:
            resp_2 = tag_image(cli, project.proname, ':1.0', 'latest')
        if resp_1 and resp_2:
            resp_3 = tag_image(cli, project.proname, ':2.0', '1.0')
        if resp_1 and resp_2 and resp_3:
            for line in cli.push(REGISTRY + project.proname, stream=True):
                # 打印出上传的log
                print line
                assert line
            project.tag = message['tagName']
            db.session.add(project)
            db.session.commit()
            socketio.emit('tag response', {'tagName': project.tag})
        print project.tag
    return json.dumps({'msg': 'ok'})


def tag_image(cli, image, old_tag, tag):
    response = cli.tag(
        image=REGISTRY + image + old_tag,
        repository=REGISTRY + image,
        tag=tag,
        force=True
    )
    return response
