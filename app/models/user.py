# -*- coding: utf-8 -*-
from app import db
from .role import RoleModel
from .permission import Permission


class UserModel(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key = True)
    nickname = db.Column(db.String(64), unique = True, index=True)
    email = db.Column(db.String(120), index = True, unique = True)
    password = db.Column(db.String(256))
    # 用户角色
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

    # 赋予角色
    def __init__(self, **kwargs):
        super(UserModel, self).__init__(**kwargs)
        if self.role is None:
            self.role = RoleModel.query.filter_by(default=True).first()

    # 验证权限
    def can(self, permissions):
        return self.role is not None and \
                (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % (self.nickname)
