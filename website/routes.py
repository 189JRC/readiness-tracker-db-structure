import os
from flask import current_app as app
from flask import render_template, request, jsonify
from website import db
from typing import Type


@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
# Now comes the actual function definition for processing this page
def index():
    # This is a vue project that serves the static index file only
    return render_template("index.html")
