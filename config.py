import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # The application entry point
    FLASK_APP = "wsgi.py"

    # Get .env variables
    SECRET_KEY = os.environ.get("SECRET_KEY")
    INSTANCE_TYPE = os.environ.get("INSTANCE_TYPE")
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
    DB_USERNAME = os.environ.get("DB_USERNAME")
    database_password = os.environ.get("database_password")
    database_address = os.environ.get("database_address")
    database_port = os.environ.get("database_port")
    database = os.environ.get("database")
    DB_TYPE = os.environ.get("DB_TYPE")

    if DB_TYPE == "mysql":
        SQLALCHEMY_DATABASE_URI = (
            "mysql+mysqlconnector://"
            + DB_USERNAME
            + ":"
            + database_password
            + "@"
            + database_address
            + ":"
            + database_port
            + "/"
            + database
            + "?charset=utf8mb4&collation=utf8mb4_general_ci"
        )

    if DB_TYPE == "postgresql":
        SQLALCHEMY_DATABASE_URI = (
            "postgresql://"
            + DB_USERNAME
            + ":"
            + database_password
            + "@"
            + database_address
            + ":"
            + database_port
            + "/"
            + database
        )


if __name__ == "__main__":
    config = Config()
