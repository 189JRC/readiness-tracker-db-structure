import os
from website import db, create_app
from website.models import User, Organisation, OrganisationHeirarchy, User_Organisation
from dotenv import load_dotenv

from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError, DataError


# Create the Flask app
app = create_app()


def add_org_heirarchy():
    with app.app_context():
        heirarchies_to_add_to_db = []
        heirarchy_lst = [
            "super user",
            "head office",
            "brand",
            "region",
            "area",
            "retailer",
        ]
        level = 100
        level_increment = 100 // len(heirarchy_lst)
        # Create a new OrganisationHeirarchy instance
        for heirarchy in heirarchy_lst:
            heirarchies_to_add_to_db.append(
                OrganisationHeirarchy(
                    name=heirarchy,
                    level=level,
                )
            )
            level -= level_increment

        # Add the new OrganisationHeirarchy to the database session
        db.session.add_all(heirarchies_to_add_to_db)

        try:
            db.session.commit()
        except Exception as e:
            print(f"Error adding records: {str(e)}")
            db.session.rollback()


def add_orgs():
    with app.app_context():
        all_heirarchy_objs = OrganisationHeirarchy.query.all()

        total_orgs_to_add = [1, 1, 3, 10, 20, 50]

        organisations_to_add_to_db = []
        org_unit_number = 1
        for index, heirarchy_level in enumerate(all_heirarchy_objs):
            for __ in range(total_orgs_to_add[index]):
                # Create a new Organisation instance referencing the OrganisationHeirarchy
                organisations_to_add_to_db.append(
                    Organisation(
                        name=f"org_unit_{org_unit_number}",
                        code=f"ORG{org_unit_number}",
                        type="Some Type",
                        organisational_heirarchy=heirarchy_level,
                    )
                )
                org_unit_number += 1

        # Add the new Organisation to the database session
        db.session.add_all(organisations_to_add_to_db)

        # Optionally, you can also handle exceptions and rollback the session in case of an error
        try:
            db.session.commit()
        except Exception as e:
            print(f"Error adding records: {str(e)}")
            db.session.rollback()


def add_users():
    with app.app_context():
        new_organisation = Organisation.query.filter_by(name="VW").first()
        # Create a new User instance
        new_user = User(
            name="test Doe",
            email="jtest@example.com",
            hashed_password=generate_password_hash("password123"),
        )

        # Add the new User to the database session
        db.session.add(new_user)

        try:
            db.session.commit()
        except Exception as e:
            print(f"Error adding User: {str(e)}")
            db.session.rollback()
            return

        # Associate the User with the Organisation
        user_organisation = User_Organisation(
            user_id=new_user.id,
            organisation_id=new_organisation.id,
        )

        # Add the User-Organisation relationship to the database session
        db.session.add(user_organisation)

        try:
            db.session.commit()
        except Exception as e:
            print(f"Error adding User-Organisation relationship: {str(e)}")
            db.session.rollback()


def delete_all_entries():
    with app.app_context():
        # Delete all entries in User_organisation table
        db.session.query(User_Organisation).delete()

        # Delete all entries in User table
        db.session.query(User).delete()

        # Delete all entries in Organisation table
        db.session.query(Organisation).delete()

        # Delete all entries in OrganisationHeirarchy table
        db.session.query(OrganisationHeirarchy).delete()

        # Commit the changes
        db.session.commit()


if __name__ == "__main__":
    # Run the create_roles function when this script is executed directly
    delete_all_entries()
    add_org_heirarchy()
    add_orgs()
    # add_users()
