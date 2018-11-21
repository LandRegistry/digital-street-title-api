import os
from flask_script import Manager
from title_api.main import app

# ***** For Alembic start ******
from flask_migrate import Migrate, MigrateCommand
from title_api.models import *    # noqa
from title_api.extensions import db

migrate = Migrate(app, db)
# ***** For Alembic end ******

# Init manager
manager = Manager(app)

# ***** For Alembic start ******
manager.add_command('db', MigrateCommand)
# ***** For Alembic end ******


@manager.command
def runserver(port=8005):
    """Run the app using flask server"""

    os.environ["PYTHONUNBUFFERED"] = "yes"
    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["COMMIT"] = "LOCAL"

    app.run(debug=True, port=int(port))


if __name__ == "__main__":
    manager.run()
