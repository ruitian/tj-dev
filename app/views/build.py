# -*- coding: utf-8 -*-
from flask_login import login_required, current_user
from flask import render_template

from app import app, oauth
from app.utils import GithubOAuth


@app.route('/build')
@login_required
def build_code():
    return render_template('build.html')


@app.route('/build/new')
@login_required
def build_code_new():
    print GithubOAuth.github.get('user').data
    return render_template('build-new.html')