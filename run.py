from app import app, db
from flask_script import Manager, Server

manager = Manager(app)
manager.add_command("runserver", Server(host="0.0.0.0", port="3000" ))

@manager.command
def deploy():
    db.drop_all()
    db.create_all()

if __name__ == '__main__':
    manager.run()
