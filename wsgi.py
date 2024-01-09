# Application entry point.
from website import create_app, db
from website.models import User, Organisation, OrganisationHeirarchy

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {
        "db": db,
        "User": User,
        "Organisation": Organisation,
        "OrganisationHeirarchy": OrganisationHeirarchy,
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
