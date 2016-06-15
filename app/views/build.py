# -*- coding: utf-8 -*-
import json
from flask_login import login_required, current_user
from flask import render_template

from app import app, redis


@app.route('/build')
@login_required
def build_code():
    return render_template('build.html')


@app.route('/build/new')
@login_required
def build_code_new():
    github_data = json.loads(redis.hget(current_user.id, 'github_data'))
    github_orgs_data = redis.hget(current_user.id, 'github_orgs_data')
    if github_orgs_data is not None:
        github_orgs_data = eval(github_orgs_data)

    # github_avatar = github_data['avatar_url']
    return render_template(
        'build-new.html',
        github_data=github_data,
        github_orgs_data=github_orgs_data
        )
