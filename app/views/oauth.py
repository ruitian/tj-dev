# -*- coding: utf-8 -*-
from flask import url_for, session, jsonify
from flask_login import current_user

from app import app, db
from app.utils import GithubOAuth


@app.route('/github/login')
def github_login():
    return GithubOAuth.github.authorize(
        callback=url_for('authorized', _external=True)
    )


@app.route('/github/login/authorized')
def authorized():
    resp = GithubOAuth.github.authorized_response()
    session['github_token'] = (resp['access_token'], '')
    current_user.github_token = resp['access_token']
    db.session.add(current_user)
    db.session.commit()
    return jsonify(GithubOAuth.github.get('user').data)


@GithubOAuth.github.tokengetter
def get_github_oauth_token():
    return session.get('github_token')
