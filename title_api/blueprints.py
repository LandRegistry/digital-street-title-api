# Import every blueprint file
from title_api.views import general, title_v1, conveyancer_v1, owner_v1


def register_blueprints(app):
    """Adds all blueprint objects into the app."""
    app.register_blueprint(general.general)
    app.register_blueprint(title_v1.title_v1, url_prefix='/v1')
    app.register_blueprint(conveyancer_v1.conveyancer_v1, url_prefix='/v1')
    app.register_blueprint(owner_v1.owner_v1, url_prefix='/v1')

    # All done!
    app.logger.info("Blueprints registered")
