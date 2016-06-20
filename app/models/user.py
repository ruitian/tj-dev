# -*- coding: utf-8 -*-
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin

from app import db, login_manager
from .role import RoleModel
from .permission import Permission


class AnonymousUser(AnonymousUserMixin):

    super

login_manager.anonymous_user = AnonymousUser


class UserModel(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(256))
    github_token = db.Column(db.String(256), default=None)
    gitlab_token = db.Column(db.String(256), default=None)
    # 用户角色
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

    # 赋予角色
    def __init__(self, **kwargs):
        super(UserModel, self).__init__(**kwargs)
        if self.role is None:
            self.role = RoleModel.query.filter_by(default=True).first()

    @login_manager.user_loader
    def load_user(id):
        return UserModel.query.get(int(id))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # 验证权限
    def can(self, permissions):
        return self.role is not None and \
                (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)
