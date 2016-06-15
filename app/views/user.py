# -*- coding: utf-8 -*-
from app import app, db
from app.forms import LoginForm, RegisterForm
from app.models import UserModel

from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, login_required


class UserService(object):

    @staticmethod
    def get_user_by_username(username):
        return UserModel.query.filter_by(username=username).first()

    @staticmethod
    def get_user_by_email(email):
        return UserModel.query.filter_by(email=email).first()

    @staticmethod
    def get_user(username_or_email):
        if '@' in username_or_email:
            return UserService.get_user_by_email(username_or_email)
        return UserService.get_user_by_username(username_or_email)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html')


@app.route('/accounts/add', methods=['GET', 'POST'])
def create_user():
    form = RegisterForm()
    if request.method == 'POST' and form.validate_on_submit:
        username = form.username.data
        email = form.email.data
        password = form.password.data
        if UserService.get_user_by_email(email) is not None:
            flash(u'邮箱已被使用')
            return redirect(url_for('create_user'))
        if UserService.get_user_by_username(username) is not None:
            flash(u'用户名已被使用', 'warning')
            return redirect(url_for('create_user'))
        user = UserModel(
            username=username,
            email=email,
            )
        user.password = password
        db.session.add(user)
        db.session.commit()
        flash(u'用户添加成功', 'success')
        redirect(url_for('create_user'))

    return render_template('register.html', form=form)


@app.route("/accounts/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit:
        username_or_email = form.username_or_email.data
        password = form.password.data
        user = UserService.get_user(username_or_email)
        if user is not None and user.verify_password(password):
            login_user(user)
            flash(u'登录成功', 'success')
            return redirect(url_for('index'))
        flash(u'用户名或密码错误', 'danger')
        return redirect(url_for('login'))
    return render_template("login.html", form=form)
