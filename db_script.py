import os
from website import db, create_app
from website.models import (
    User,
    Organisation,
    OrganisationHeirarchy,
    User_Organisation,
    OrganisationOrganisation,
    Project,
    ProjectOrganisation,
)

from dotenv import load_dotenv

from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError, DataError
from faker import Faker
import random

fake = Faker()

# Create the Flask app
app = create_app()

heirarchy_lst = [
    "super user",
    "head office",
    "brand",
    "region",
    "area",
    "retailer",
]


def add_org_heirarchy():
    heirarchies_to_add_to_db = []
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
    users_to_add_to_db = []
    no_of_users_to_add = 3 * len(heirarchy_lst)

    for _ in range(no_of_users_to_add):
        users_to_add_to_db.append(
            User(
                name=fake.name(),
                email=fake.email(),
                hashed_password=generate_password_hash(fake.password(length=12)),
            )
        )

    # Add the new User to the database session
    db.session.add_all(users_to_add_to_db)

    try:
        db.session.commit()
    except Exception as e:
        print(f"Error adding User: {str(e)}")
        db.session.rollback()
        return


def assign_users_to_orgs():
    all_users = User.query.all()
    all_organisations = Organisation.query.all()

    users_per_org = 3

    for org in all_organisations:
        users_for_org = all_users[:users_per_org]
        all_users = all_users[users_per_org:]

        for user in users_for_org:
            user_org_relationship = User_Organisation(
                user_id=user.id, organisation_id=org.id
            )
            db.session.add(user_org_relationship)

    try:
        db.session.commit()
    except Exception as e:
        print(f"Error assigning users to organizations: {str(e)}")
        db.session.rollback()


def create_initial_org_groups():
    # Loop through org heirarchy table (reversed)
    all_heirarchies = OrganisationHeirarchy.query.all()

    for heirarchy in all_heirarchies[::-1]:
        if heirarchy.name == "super user":
            break
        orgs_to_assign_parent = Organisation.query.filter_by(
            organisational_heirarchy_id=heirarchy.id
        ).all()

        parent_orgs = Organisation.query.filter_by(
            organisational_heirarchy_id=(heirarchy.id - 1)
        ).all()

        for org in orgs_to_assign_parent:
            org_org_relationship = OrganisationOrganisation(
                parent_organisation_id=random.choice(parent_orgs).id,
                child_organisation_id=org.id,
            )
            db.session.add(org_org_relationship)

    try:
        db.session.commit()
    except Exception as e:
        print(f"Error assigning users to organizations: {str(e)}")
        db.session.rollback()


def make_projects_visibile_to_children(new_project, parent_org):
    # Step 3: Recursively populate ProjectOrganisation with project ID for all descendants
    def populate_project_organisation(project, parent_org):
        try:
            children = (
                db.session.query(Organisation)
                .join(
                    OrganisationOrganisation,
                    Organisation.id == OrganisationOrganisation.child_organisation_id,
                )
                .filter(
                    OrganisationOrganisation.parent_organisation_id == parent_org.id
                )
                .all()
            )
        except:
            children = []

        project_org_relationships = []
        for child_org in children:
            project_org_relationship = ProjectOrganisation(
                organisation_id=child_org.id,
                project_id=project.id,
                only_visible=False,  # Make the project visible to children
            )
            project_org_relationships.append(project_org_relationship)

        db.session.add_all(project_org_relationships)

        # Recursively call the function for each child
        for child_org in children:
            populate_project_organisation(project, child_org)

    # Call the recursive function to populate ProjectOrganisation
    populate_project_organisation(new_project, parent_org)


def create_project():
    project_setters = ["head office", "area"]

    for setter in project_setters:
        # Step 1: Retrieve the Head Office organization
        heirarchy_obj = OrganisationHeirarchy.query.filter_by(name=setter).first()

        org = Organisation.query.filter_by(
            organisational_heirarchy_id=heirarchy_obj.id
        ).first()

        # Step 2: Create a new project
        new_project = Project(
            name=f"{setter} Project",
            description=f"This {setter} project will be seen by all children",
            organisation_id=org.id,
        )

        db.session.add(new_project)

        try:
            db.session.commit()
        except Exception as e:
            print(f"Error creating project: {str(e)}")
            db.session.rollback()
            return

        make_projects_visibile_to_children(new_project, org)

    try:
        db.session.commit()
    except Exception as e:
        print(f"Error populating ProjectOrganisation: {str(e)}")
        db.session.rollback()


def delete_all_entries():
    # Delete all entries in User_organisation table
    db.session.query(User_Organisation).delete()

    # Delete all entries in User table
    db.session.query(User).delete()

    # Delete all entries in Organisation table
    db.session.query(Organisation).delete()

    # Delete all entries in OrganisationHeirarchy table
    db.session.query(OrganisationHeirarchy).delete()

    # Delete all entries in Organisation_Organisation table
    db.session.query(OrganisationOrganisation).delete()

    # Delete all entries in ProjectOrganisation table
    db.session.query(ProjectOrganisation).delete()

    # Delete all entries in Project table
    db.session.query(Project).delete()

    # Commit the changes
    db.session.commit()


if __name__ == "__main__":
    with app.app_context():
        # Run the create_roles function when this script is executed directly
        delete_all_entries()
        add_org_heirarchy()
        add_orgs()
        add_users()
        assign_users_to_orgs()
        create_initial_org_groups()
        create_project()
