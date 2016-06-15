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
    redis.hset(
        current_user.id,
        'github_data',
        json.dumps(GithubOAuth.github.get('user').data))
    redis.hset(
        current_user.id,
        'github_orgs_data',
        urllib2.urlopen(
            'https://api.github.com/user/orgs?access_token=%s'
            % resp['access_token']).read()
        )
    return redirect(url_for('build_code_new'))


@GithubOAuth.github.tokengetter
def get_github_oauth_token():
    return (current_user.github_token, '')
