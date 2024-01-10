import os
from flask import current_app as app
from flask import render_template, request, jsonify
from website import db
from typing import Type
from website.models import (
    User,
    OrganisationHeirarchy,
    Organisation,
    User_Organisation,
    OrganisationOrganisation,
    Project,
)


@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
# Now comes the actual function definition for processing this page
def index():
    # This is a vue project that serves the static index file only
    return render_template("index.html")

@app.route("/users", methods=["GET"])
def get_users():

    """#would full row for a db entry ever be required?
    #how else to achieve other than with loop to cycle through a dict entry within a loop of returned objects?
    # all_columns = []
    # sample_user = User.query.first()
    # for field, value in sample_user.__dict__.items():
    #     all_columns.append(field)

    # users = User.query.all() 
    # users_list = []"""
    
    users = User.query.all()
    #serialise the dicts by id for desired json format
    users_list_by_id = {user.id: {'username': user.name, 'email': user.email, 'is_deleted': user.is_deleted, 'created_timestamp': user.created_timestamp} for user in users}
    return jsonify(users = users_list_by_id)

@app.route("/users/<int:id>", methods=["GET"])
def get_user_by_id(id):

    requested_user = User.query.get(id)
    if requested_user:
        pass
    else:
        return "404"
    
    requested_user = {'id': requested_user.id, 'username': requested_user.name, 'email': requested_user.email, "created_timestamp": requested_user.created_timestamp}
    return jsonify(requested_user)
