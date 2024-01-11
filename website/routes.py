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

def ensure_ho_user(func):
    def wrapper(*args, **kwargs):
        # Code to run before the route function is executed
        print("Decorator Code Before Function Execution")
        
        # Call the original route function
        result = func(*args, **kwargs)
        
        # Code to run after the route function is executed
        print("Decorator Code After Function Execution")
        
        return result

    return wrapper


@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
# Now comes the actual function definition for processing this page
def index():
    # This is a vue project that serves the static index file only
    return render_template("index.html")


@app.route("/users", methods=["GET"])
@ensure_ho_user
def get_users():
    """API route to allow an authorised HO user to access records for all users"""

    #Return value
    #what fields are required for json data
    #what index value to use in json

    # [STANDARD BLOCK/Decorator wrapped] (a guard barrier to restrict access to only authorised users)
    # user = get_user_from_request(request)
    user = {"logged_in":True}

    if not user["logged_in"]:
        # any use in logging failed requests when this conditional is executed?
        return dict(
            rc=16,
            message=f"You do not have the correct authorisation for this api",
        )

    # [STANDARD BLOCK] guard barrier such that only authenticated HO users can pass
    user = get_user_from_request(request)
    if not user["logged_in"]:
        # I previously logged this situation but it henerates many false problems.
        # The serious ones are logged by get_user_from_request
        return dict(
            rc=16,
            message=f"You do not have the correct authorisation for this api",
        )
    
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



def get_user_from_request(request, refresh_session_jwt=False, mfa_required=True):

    # Every api needs a legitimiate user to be signed in and to have a
    # properly encoded jwt
    # If the jwt is missing or invalid (other than being timed out) then
    # the reponse is throttled with a 1 second sleep
    """
    There are further enhancement that we can do to improve security
    1   Always verify this is a POST reuest and discard anything that is not
    2   Verify the source origin and the target origin match
    todo: further investigate and deploy if suitable
    """

    api_package = request.get_json()

    user = dict(id='', logged_in=False, role_name=None)

    # make sure we have a session and a mfa jwt - bounce if not
    try:
        session_jwt = api_package["session_jwt"]
        decoded_session_jwt = jwt.decode(
            session_jwt, app.secret_key, algorithms="HS512"
        )
        user_from_db_via_orm = User.get_user_by_email(
            decoded_session_jwt["email"])

    except Exception as err:
        return user

    # If we have come from api_get_user, we must bounce if we don't have a valid mfa_jwt
    if request.endpoint == "api_get_user":
        try:
            mfa_jwt = api_package["mfa_jwt"]
            decoded_mfa_jwt = jwt.decode(
                mfa_jwt, app.secret_key, algorithms="HS512")

            # now check that this user has the correct email address
            if not decoded_mfa_jwt["email"] == decoded_session_jwt["email"]:
                return dict(logged_in=False, role_name=None)

            # commented out by Ivan as part of ip address bug fix June 2023
            # if not decoded_mfa_jwt["ip_address"] == decoded_session_jwt["ip_address"]:
            #     return dict(logged_in=False, role_name=None)

            if not decoded_mfa_jwt["mfa_secret_encrypted"] == user_from_db_via_orm.mfa_secret:
                return dict(logged_in=False, role_name=None)

            # If we get to here then the frequent check on the user is ok as far as mfa is concerned

            you_can_break_here = True

        except Exception as err:
            return dict(logged_in=False, role_name=None)

    # so we have an decoded_session_jwt - let's see if it any good

    try:

        now = datetime.datetime.now(tz=datetime.timezone.utc).timestamp()

        if user_from_db_via_orm.is_deleted:
            user["logged_in"] = False
        else:

            if "email" in decoded_session_jwt:
                user["email"] = decoded_session_jwt["email"]

            user["logged_in"] = True

            # get the role_name from the user.role_id
            role = Role.query.filter_by(
                id=user_from_db_via_orm.role_id,
                is_deleted=False,
            ).first()

             # get the role_name from the ser_from_db_via_orm.id
            user["id"] = user_from_db_via_orm.id

            user["role_name"] = role.name

            if "loggedOnAtSeconds" in decoded_session_jwt:
                user["seconds_remaining"] = int(
                    SESSION_EXPIRES_SECONDS
                    - (now - decoded_session_jwt["loggedOnAtSeconds"])
                )

            # if "ip_address" in decoded_session_jwt:
            #     user["ip_address"] = decoded_session_jwt["ip_address"]

    except Exception as err:
        try:
            if err.args[0] == "Signature has expired":
                pass
            elif err.args[0] == "Signature verification failed":
                # throttle the responses
                # We need to do a throttle here that will not block the whole flask process
                app.logger.warning(
                    f"[WARNING] err was {err} - can come from corrupted jwt if it happens often then could be attack"
                )
        except:
            # throttle the responses
            # We need to do a throttle here that will not block the whole flask process
            app.logger.exception(f"[EXCEPTION] err was {err}")

    return user


