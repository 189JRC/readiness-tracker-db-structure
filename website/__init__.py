import os
import platform
import socket
from flask import Flask, jsonify, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config


db = SQLAlchemy()

migrate = Migrate()

# create the holder for site config stuff
site_config = {}
site_config["platform"] = platform.system()
site_config["base_directory"] = os.path.abspath(os.path.dirname(__file__))
site_config["host_name"] = socket.gethostname()
site_config[
    "environment"
] = f'host:{site_config["host_name"]}, platform:{site_config["platform"]}'
site_config["INSTANCE_TYPE"] = os.environ.get("INSTANCE_TYPE")
site_config["this_url"] = os.environ.get("this_url")


def create_app():
    # This constructs the Flask application instance, and eliminates using it as a global variable, which can cause issues

    # Set the paths so that Flask knows where to look to serve up the static files
    this_directory = os.path.abspath(os.path.dirname(__file__))
    static_folder = os.path.join(this_directory, "templates", "static")
    app = Flask(
        __name__,
        instance_relative_config=False,
        static_folder=static_folder,
        static_url_path="/static",
    )

    app.config.from_object("config.Config")

    with app.app_context():
        # now all the initiations
        db.init_app(app)
        migrate.init_app(app, db=db)

        # import the routes
        from website import routes, models

        # all is set up correctly so return the app
        return app
