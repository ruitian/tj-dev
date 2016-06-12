# -*- coding: utf-8 -*-
from app import db
from .permission import Permission


# 用户角色表
class RoleModel(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('UserModel', backref='role', lazy='dynamic')

    # 写入权限
    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.COMMON, True),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = RoleModel.query.filter_by(name=r).first()
            if role is None:
                role = RoleModel(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()
