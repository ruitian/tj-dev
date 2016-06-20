# -*- coding: utf-8 -*-
import json
from flask_login import login_required, current_user
from flask import render_template

from app import app, redis

false = False
null = None
true = True

@app.route('/build')
@login_required
def build_code():
    return render_template('build.html')


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
