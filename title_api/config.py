import os

# RULES OF CONFIG:
# 1. No region specific code. Regions are defined by setting the OS environment variables appropriately to build up the
# desired behaviour.
# 2. No use of defaults when getting OS environment variables. They must all be set to the required values prior to the
# app starting.
# 3. This is the only file in the app where os.environ should be used.

# --- Database variables start

# These must all be set in the OS environment.
# The password must be the correct one for either the app user or alembic user,
# depending on which will be used (which is controlled by the SQL_USE_ALEMBIC_USER variable)

SQL_HOST = os.environ['SQL_HOST']
SQL_DATABASE = os.environ['SQL_DATABASE']
SQL_PASSWORD = os.environ['SQL_PASSWORD']
APP_SQL_USERNAME = os.environ['APP_SQL_USERNAME']
ALEMBIC_SQL_USERNAME = os.environ['ALEMBIC_SQL_USERNAME']

if os.environ['SQL_USE_ALEMBIC_USER'] == 'yes':
    FINAL_SQL_USERNAME = ALEMBIC_SQL_USERNAME
else:
    FINAL_SQL_USERNAME = APP_SQL_USERNAME

SQLALCHEMY_DATABASE_URI = 'postgres://{0}:{1}@{2}/{3}'.format(FINAL_SQL_USERNAME, SQL_PASSWORD, SQL_HOST, SQL_DATABASE)
SQLALCHEMY_TRACK_MODIFICATIONS = False  # Explicitly set this in order to remove warning on run
SQLALCHEMY_POOL_RECYCLE = int(os.environ['SQLALCHEMY_POOL_RECYCLE'])


# For the enhanced logging extension
FLASK_LOG_LEVEL = os.environ['LOG_LEVEL']

# For health route
COMMIT = os.environ['COMMIT']

# This APP_NAME variable is to allow changing the app name when the app is running in a cluster. So that
# each app in the cluster will have a unique name.
APP_NAME = os.environ['APP_NAME']
MAX_HEALTH_CASCADE = int(os.environ['MAX_HEALTH_CASCADE'])
DEFAULT_TIMEOUT = int(os.environ['DEFAULT_TIMEOUT'])

# Following is an example of building the dependency structure used by the cascade route
# SELF can be used to demonstrate how it works (i.e. it will call it's own casecade
# route until MAX_HEALTH_CASCADE is hit)
# SELF = "http://localhost:8080"
DEPENDENCIES = {"Postgres": SQLALCHEMY_DATABASE_URI}

# Using SQLAlchemy/Postgres?
# The required variables (and required usage) can be found here:
# http://git.dev.ctp.local/gadgets/gadget-api/blob/master/gadget_api/config.py
