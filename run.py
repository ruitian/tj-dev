from app import app, db, socketio
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand


def make_shell_context():
    return dict(
        app=app,
        db=db
    )
manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command("runserver", socketio.run(app, host="0.0.0.0", port=5000))
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command("db", MigrateCommand)


@manager.command
def deploy():
    db.drop_all()
    db.create_all()

if __name__ == '__main__':
    manager.run()
