from flask import current_app as app, jsonify
from flask import redirect, Blueprint, request, session, url_for, render_template
from saml2 import entity
from flask import url_for, current_app as app
from saml2 import BINDING_HTTP_REDIRECT, BINDING_HTTP_POST
from saml2.client import Saml2Client
from saml2.config import Config as Saml2Config
from functools import wraps
import json
import os
import sys

def init_saml_client():
    """
    Given the name of an IdP, return a configuation.
    The configuration is a hash for use by saml2.config.Config
    """

    acs_url = url_for("sso.sp_initiated", _external=True)
    https_acs_url = url_for("sso.sp_initiated", _external=True, _scheme="https")

    try:
        # Override the metadata file path with this environment variable.
        print(os.path.join(sys.path[0], "./metadata.xml"))
        with open(os.path.join(sys.path[0], "./metadata.xml")) as f:
            inline = f.read()
    except Exception as e:
        raise Exception("Failed to read SAML metadata. %s" % e)

    settings = {
        "entityid":"https://adobe.okta.com/api/v1/apps/0oa1iujaheoHZ2AZ20h8/sso/saml/metadata",
        "metadata": {"inline": [inline]},
        "service": {
            "sp": {
                "endpoints": {
                    "assertion_consumer_service": [
                        (acs_url, BINDING_HTTP_REDIRECT),
                        (acs_url, BINDING_HTTP_POST),
                        (https_acs_url, BINDING_HTTP_REDIRECT),
                        (https_acs_url, BINDING_HTTP_POST),
                    ]
                },
                "allow_unsolicited": True,
                # Don't sign authn requests, since signed requests only make
                # sense in a situation where you control both the SP and IdP
                "authn_requests_signed": False,
                "logout_requests_signed": True,
                "want_assertions_signed": True,
                "want_response_signed": False,
            }
        },
    }
    spConfig = Saml2Config()
    spConfig.load(settings)
    spConfig.allow_unknown_attributes = True
    saml_client = Saml2Client(config=spConfig)

    return saml_client


sso = Blueprint("sso", __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' in session:
            session.permanent = True
            return f(*args, **kwargs)
        else:
            return redirect(url_for('.sp_initiated'))
    return decorated_function

@sso.route("/")
def getHome():
    return render_template('index.html', username = session["username"])


@sso.route("/sso/saml/login", methods=["POST"])
def idp_initiated():
    # This is the endpoint where the end user browser will POST to after completing the Okta flow.
    saml_client = init_saml_client()

    # If the authentication fails, this will raise.
    authn_response = saml_client.parse_authn_request_response(
        request.form["SAMLResponse"], entity.BINDING_HTTP_POST
    )

    # This will populate the authn_response object
    authn_response.get_identity()
    user_info = authn_response.get_subject()

    # Custom attributes defined on oss.corp.adobe.com will be available here
    username = authn_response.ava["UserID"][0]
    email = authn_response.ava["Email"][0].lower()
    # At this point the user is authenticated, create a session, redirect to page, anything...
    session['username'] = username
    session['email'] = email
    return redirect(url_for('.getHome'))
    # return jsonify(authn_response.ava), 200


@sso.route("/sso/saml/login", methods=["GET"])
def sp_initiated():
    # Redirect the end user to Okta authentication flow.
    saml_client = init_saml_client()
    reqid, info = saml_client.prepare_for_authenticate()
    redirect_url = None
    for key, value in info['headers']:
        if key is 'Location':
            redirect_url = value
    response = redirect(redirect_url, code=302)
    response.headers['Cache-Control'] = 'no-cache, no-store'
    response.headers['Pragma'] = 'no-cache'
    return response