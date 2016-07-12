# -*- coding: utf-8 -*-
import json
from app import app, db
from app.forms import LoginForm, RegisterForm
from app.models import UserModel

from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, login_required, current_user


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
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if UserService.get_user_by_email(email) is not None:
            flash(u'邮箱已被使用', 'danger')
            return redirect(url_for('user_profile'))
        if UserService.get_user_by_username(username) is not None:
            flash(u'用户名已被使用', 'danger')
            return redirect(url_for('user_profile'))
        user = UserModel(
            username=username,
            email=email,
            )
        user.password = password
        db.session.add(user)
        db.session.commit()
        flash(u'用户添加成功', 'success')
        return redirect(url_for('user_profile'))


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


@app.route("/accounts/profile", methods=['GET', 'POST'])
@login_required
def user_profile():
    if current_user.is_administrator():
        users = UserModel.query.order_by(UserModel.id.desc())
        return render_template('admin.html', users=users)
    else:
        return render_template('profile.html')


@app.route("/accounts/profile/setting", methods=['GET', 'POST'])
@login_required
def user_profile_setting():
    username = request.form['username']
    password = request.form['password']
    user = UserModel.query.filter_by(username=username).first()
    user.password = password
    db.session.add(user)
    db.session.commit()
    flash(u'修改成功!', 'success')
    return redirect(url_for('user_profile'))


@app.route('/accounts/search', methods=['POST'])
@login_required
def search_user():
    username = json.loads(request.get_data())['data']
    user = UserModel.query.filter_by(username=username).first()
    if user is None:
        return json.dumps({'msg': 0})
    else:
        return json.dumps({'msg': 1, 'username': user.username, 'email': user.email})


@app.route('/accounts/profile/modify', methods=['GET', 'POST'])
@login_required
def user_profile_modify():
    print 123
    username = request.form['username']
    old_pass = request.form['old-password']
    new_pass = request.form['new-password']
    user = UserModel.query.filter_by(username=username).first()
    if not user.verify_password(old_pass):
        flash(u'原密码不匹配', 'danger')
        return redirect(url_for('user_profile'))
    else:
        user.password = new_pass
        db.session.add(user)
        db.session.commit()
        flash(u'修改成功', 'success')
        return redirect(url_for('user_profile'))

