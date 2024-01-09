# As a one off when the app is first created:
# Navigate to back_end
# type: python -m  flask db init
#
# When you make updates to the models in this file, you need to bring the database into sync with it
# open a terminal with the correct environment activated
# type: python -m flask db migrate -m "Initial migration."
#
# Then check the sql update statements in the script that was generated in the migrations folder
# NB This is an important check, not a cursory glance!
# NB They might be wrong!
#
# When you are confident they are correct,
# type: python -m flask db upgrade
#
# The database is now updated to reflect this model file


import os
from datetime import datetime, timedelta
from flask import current_app as app
from website import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import func, expression, and_, or_


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=False, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    hashed_password = db.Column(db.String(200), unique=False, nullable=False)
    cc_emails = db.Column(db.String(1000), unique=False, nullable=True)
    failed_login_streak = db.Column(db.Integer, server_default="0")
    mfa_secret = db.Column(db.String(100), unique=False, nullable=True)
    mfa_secret_confirmed = db.Column(
        db.BOOLEAN, nullable=False, server_default=expression.false()
    )
    is_deleted = db.Column(
        db.BOOLEAN, nullable=False, server_default=expression.false()
    )
    pii_key_id = db.Column(db.Integer, index=True, nullable=False, server_default="0")
    created_timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return "<User {}>".format(self.name)


# One to many relationship between OrganisationHeirarchy and Organisation
class OrganisationHeirarchy(db.Model):
    __tablename__ = "organisation_heirarchy"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    level = db.Column(db.Integer, unique=True, nullable=False)
    is_deleted = db.Column(db.Boolean, nullable=False, server_default=db.text("false"))
    created_timestamp = db.Column(
        db.DateTime(timezone=True), server_default=db.func.now()
    )
    # Define the relationship back-reference
    organisations = relationship("Organisation", backref="organisational_heirarchy")


class Organisation(db.Model):
    __tablename__ = "organisations"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    code = db.Column(db.String(30), unique=True, nullable=False)
    type = db.Column(db.String(30), nullable=False)
    is_deleted = db.Column(db.Boolean, nullable=False, server_default=db.text("false"))
    created_timestamp = db.Column(
        db.DateTime(timezone=True), server_default=db.func.now()
    )

    # Maps to the organisation_heirarchy table
    organisational_heirarchy_id = db.Column(
        db.Integer, ForeignKey("organisation_heirarchy.id")
    )


# Many to many relationship table
class User_Organisation(db.Model):
    __tablename__ = "users_organisations"
    __table_args__ = (
        db.UniqueConstraint(
            "user_id", "organisation_id", name="unique_user_organisation"
        ),
    )
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", name=f"fk_{__tablename__}_users", ondelete="CASCADE"),
        nullable=False,
    )
    organisation_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "organisations.id",
            name=f"fk_{__tablename__}_organisations",
            ondelete="CASCADE",
        ),
        nullable=True,
    )
    is_deleted = db.Column(
        db.BOOLEAN, nullable=False, server_default=expression.false()
    )
    created_timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())


class OrganisationOrganisation(db.Model):
    __tablename__ = "organisations_organisations"
    __table_args__ = (
        db.UniqueConstraint(
            "parent_organisation_id",
            "child_organisation_id",
            name="unique_parent_child_organisation",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    parent_organisation_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "organisations.id",
            name=f"fk_{__tablename__}_parent_organisations",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    child_organisation_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "organisations.id",
            name=f"fk_{__tablename__}_child_organisations",
            ondelete="CASCADE",
        ),
        nullable=True,
    )
    group_name = db.Column(db.String(100), nullable=False, default="default")
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)
    created_timestamp = db.Column(db.TIMESTAMP(timezone=True), default=db.func.now())


class Project(db.Model):
    __tablename__ = "projects"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(200), unique=True, nullable=False)
    is_deleted = db.Column(db.Boolean, nullable=False, server_default=db.text("false"))
    created_timestamp = db.Column(
        db.DateTime(timezone=True), server_default=db.func.now()
    )

    # Maps to the organisation table
    organisation_id = db.Column(
        db.Integer,
        ForeignKey(
            "organisations.id",
            name=f"fk_{__tablename__}_organisations",
            ondelete="CASCADE",
        ),
    )


class ProjectOrganisation(db.Model):
    __tablename__ = "projects_organisations"
    __table_args__ = (
        db.UniqueConstraint(
            "organisation_id",
            "project_id",
            name="unique_project_organisation",
        ),
    )
    id = db.Column(db.Integer, primary_key=True)
    organisation_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "organisations.id",
            name=f"fk_organisations",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    project_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "projects.id",
            name=f"fk_projects",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    only_visible = db.Column(db.Boolean, nullable=False, default=False)
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)
    created_timestamp = db.Column(db.TIMESTAMP(timezone=True), default=db.func.now())
