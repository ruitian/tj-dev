# -*- coding: utf-8 -*-
from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from .forms import LoginForm
from .models import User, ROLE_USER, ROLE_ADMIN
from app import login_manager

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/')
@app.route('/index')
@login_required
def index():
    user = g.user
    posts = [
            {
                'author': { 'nickname': 'John' },
                'body': 'Beautiful day in Portland!'
                },
            {
                'author': { 'nickname': 'Susan' },
                'body': 'The Avengers movie was so cool!'
                }
            ]
    return render_template('index.html',
            title = 'Home',
            user = user,
            posts = posts)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if g.user is not None and g.user is_authenticated:
        return redirect(url_for('index'))
    if form.validate_on_submit():
        login_user(user)
        flash("Logged in successfully.")
        return redirect(request.args.get("next") or url_for("index")
    return render_template("login.html", form=form)

