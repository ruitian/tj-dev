# -*- coding: utf-8 -*-
import urllib2
import urllib
import json
from flask import url_for, session, redirect, request
from flask_login import current_user, login_required

from app import app, db, redis
from app.utils import GithubOAuth, GitlabOAuth

false = False
null = None
true = True

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
            'https://api.github.com/user/orgs?access_token=%s&per_page=100' % resp['access_token']).read()
        )
    # 缓存个人项目信息
    redis.hset(
        current_user.id,
        'github_user_repos',
        urllib2.urlopen(
            'https://api.github.com/user/repos?access_token=%s&type=owner&per_page=100' % resp['access_token']).read()
        )
    # 缓存组织的项目信息
    github_orgs_data = redis.hget(current_user.id, 'github_orgs_data')
    if github_orgs_data is not None:
        github_orgs_data = eval(github_orgs_data)
        for github_org_data in github_orgs_data:
            redis.hset(
                current_user.id,
                github_org_data['login'],
                urllib2.urlopen(github_org_data['repos_url'] + '?per_page=100').read()
                )
    # 目前只是缓存所有的个人项目,其中包括组织中的所有项目，key 为项目的名称
    github_user_repos = redis.hget(
        current_user.id,
        'github_user_repos'
        )
    if github_user_repos is not None:
        github_user_repos = eval(github_user_repos)
        for github_user_repo in github_user_repos:
            redis.hset(
                current_user.id,
                github_user_repo['name'],
                github_user_repo['clone_url']
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
    req_url = "http://code.smartstudy.com/oauth/token"
    back_url = 'http://127.0.0.1:5000/gitlab/login/authorized'
    code = request.args.get('code')
    print code
    data = {
        'client_id':
            '675532f089b661c350f5b7f1be143145353124cca44ecdae1391d8cb8419e4e9',
        'client_secret':
            '290e4d19ff457771d6947f646c649a8ce4aade8c4e3f0d2c633c6df6f4581507',
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
            'http://code.smartstudy.com/api/v3/user?access_token=%s'
            % back_data['access_token']
        ).read()
    )
    # 缓存个人项目信息
    redis.hset(
        current_user.id,
        'gitlab_user_repos',
        urllib2.urlopen(
            'http://code.smartstudy.com/api/v3/projects?access_token=%s'
            % back_data['access_token']
            ).read()
        )
    # 目前只是缓存所有的个人项目，key 为项目的名称
    repos = urllib2.urlopen(
        'http://code.smartstudy.com/api/v3/projects?access_token=%s'
        % back_data['access_token']
        ).read()
    if repos is not None:
        repos = eval(repos)
        for repo in repos:
            redis.hset(
                current_user.id, repo['name'], repo['http_url_to_repo'])
    return redirect(url_for('build_code_new'))


def post(url, data):
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    return response.read()
