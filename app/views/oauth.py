# -*- coding: utf-8 -*-
import urllib2, urllib
import json
from flask import url_for, session, redirect, request
from flask_login import current_user, login_required

from app import app, db, redis
from app.utils import GithubOAuth, GitlabOAuth


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


@app.route('/gitlab/login')
@login_required
def gitlab_login():
    return GitlabOAuth.gitlab.authorize(
        callback=url_for('gitlab_authorized', _external=True)
    )


@app.route('/gitlab/login/authorized')
@login_required
def gitlab_authorized():
    req_url = "https://gitlab.com/oauth/token"
    back_url = 'http://localhost:5000/gitlab/login/authorized'
    code = request.args.get('code')
    data = {
        'client_id': '66dcd9cea621513f6ed2b0ee7bd84eb32fb559ee3a7d4b4a63c38d61103d0bfa',
        'client_secret': 'c5043ac0701b80b880fd1e6c81feff2c785a8024e09e1c370df00136204cd7dc',
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': back_url
    }
    post_data = urllib.urlencode(data)
    back_data = eval(post(req_url, post_data))
    current_user.gitlab_token = back_data['access_token']
    db.session.add(current_user)
    db.session.commit()
    # 缓存个人信息
    redis.hset(
        current_user.id,
        'gitlab_data',
        urllib2.urlopen(
            'https://gitlab.com/api/v3/user?access_token=%s' % back_data['access_token']
        ).read()
    )
    # 缓存个人项目信息
    redis.hset(
        current_user.id,
        'gitlab_user_repos',
        urllib2.urlopen(
            'https://gitlab.com/api/v3/projects?access_token=%s' % back_data['access_token']
            ).read()
        )
    return redirect(url_for('build_code_new'))


def post(url, data): 
    req = urllib2.Request(url, data) 
    response = urllib2.urlopen(req)
    return response.read() 
