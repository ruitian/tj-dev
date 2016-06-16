# -*- coding: utf-8 -*-
import urllib2
import json
from flask import url_for, session, redirect
from flask_login import current_user, login_required

from app import app, db, redis
from app.utils import GithubOAuth


@app.route('/github/login')
@login_required
def github_login():
    return GithubOAuth.github.authorize(
        callback=url_for('github_authorized', _external=True)
    )


@app.route('/github/login/authorized')
@login_required
def github_authorized():
    resp = GithubOAuth.github.authorized_response()
    session['github_token'] = (resp['access_token'], '')
    current_user.github_token = resp['access_token']
    db.session.add(current_user)
    db.session.commit()
    # 缓存个人的基本信息
    redis.hset(
        current_user.id,
        'github_data',
        json.dumps(GithubOAuth.github.get('user').data))
    # 缓存拥有的组织的基本信息
    redis.hset(
        current_user.id,
        'github_orgs_data',
        urllib2.urlopen(
            'https://api.github.com/user/orgs?access_token=%s&per_page=100'
            % resp['access_token']).read()
        )
    # 缓存个人项目信息
    redis.hset(
        current_user.id,
        'github_user_repos',
        urllib2.urlopen(
            'https://api.github.com/user/repos?access_token=%s&type=owner&per_page=100'
            % resp['access_token']).read()
        )
    # 缓存组织的项目信息
    github_orgs_data = redis.hget(current_user.id, 'github_orgs_data')
    if github_orgs_data is not None:
        github_orgs_data = eval(github_orgs_data)
        for github_org_data in github_orgs_data:
            print type(github_org_data)
            redis.hset(
                current_user.id,
                github_org_data['login'],
                urllib2.urlopen(github_org_data['repos_url']+'?per_page=100').read()
                )
    return redirect(url_for('build_code_new'))


@GithubOAuth.github.tokengetter
def get_github_oauth_token():
    return (current_user.github_token, '')
