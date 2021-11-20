import os
import flask
import requests
import pickle
import json

import google.oauth2.credentials
import google_auth_oauthlib.flow

from flask import request

from gmail_client import GmailClient
from task_mgr import TaskMgr, data_sync_task
from mongo_client import MongoDBClient

# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
CLIENT_SECRETS_FILE = "client_secret.json"

# token file.
ACCESS_TOKEN_FILE = "token.pickle"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
API_SERVICE_NAME = 'gmail'
API_VERSION = 'v1'

app = flask.Flask(__name__)
# Note: A secret key is included in the sample so that it works.
# If you use this code in your application, replace this with a truly secret
# key. See https://flask.palletsprojects.com/quickstart/#sessions.
app.secret_key = 'REPLACE ME - this value is here as a placeholder.'

task_manager = TaskMgr()
mdb_client = MongoDBClient()

@app.route('/')
def index():
    return print_index_table()


@app.route('/labels')
def list_tables():
    # TODO: redirect to authorize if token not found.
    credentials = None
    with open(ACCESS_TOKEN_FILE, "rb") as tf:
        credentials = pickle.load(tf)
    print(credentials)
    gmc = GmailClient(credentials)
    results = gmc.list_labels()
    return flask.jsonify(**results)


@app.route('/emails')
def list_emails():
    # TODO: redirect to authorize if token not found.
    credentials = None
    with open(ACCESS_TOKEN_FILE, "rb") as tf:
        credentials = pickle.load(tf)
    print(credentials)
    gmc = GmailClient(credentials)
    emails = gmc.list_emails()
    return json.dumps(emails)


@app.route('/email')
def get_mail():
    # TODO: redirect to authorize if token not found.
    msg_id = request.args.get("msgId")
    credentials = None
    with open(ACCESS_TOKEN_FILE, "rb") as tf:
        credentials = pickle.load(tf)
    print(credentials)
    gmc = GmailClient(credentials)
    msg = gmc.get_message(msg_id)
    return json.dumps(msg)


@app.route('/authorize')
def authorize():
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)

    # The URI created here must exactly match one of the authorized redirect URIs
    # for the OAuth 2.0 client, which you configured in the API Console. If this
    # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
    # error.
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')

    # Store the state so the callback can verify the auth server response.
    flask.session['state'] = state

    return flask.redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = flask.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    flask.session['credentials'] = credentials_to_dict(credentials)

    with open(ACCESS_TOKEN_FILE, "wb") as tf:
        pickle.dump(credentials_to_dict(credentials), tf)

    return flask.redirect(flask.url_for('test_api_request'))


@app.route('/revoke')
def revoke():
    if 'credentials' not in flask.session:
        return ('You need to <a href="/authorize">authorize</a> before ' +
                'testing the code to revoke credentials.')

    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])

    rev = requests.post('https://oauth2.googleapis.com/revoke',
                        params={'token': credentials.token},
                        headers={'content-type': 'application/x-www-form-urlencoded'})

    status_code = getattr(rev, 'status_code')
    if status_code == 200:
        return 'Credentials successfully revoked.' + print_index_table()
    else:
        return 'An error occurred.' + print_index_table()


@app.route('/clear')
def clear_credentials():
    if 'credentials' in flask.session:
        del flask.session['credentials']
    return ('Credentials have been cleared.<br><br>' +
            print_index_table())


@app.route('/data-sync')
def data_sync():
    task_manager.execute_task(data_sync_task)
    return 'Successfully started a task to sync emails from Gmail.'


@app.route('/data-sync-status')
def data_sync_status():
    sync_status = mdb_client.get_sync_status()
    return json.dumps(sync_status)


def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}


def print_index_table():
    return app.send_static_file("index.html")


if __name__ == '__main__':
    # When running locally, disable OAuthlib's HTTPs verification.
    # ACTION ITEM for developers:
    #     When running in production *do not* leave this option enabled.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    # Specify a hostname and port that are set as a valid redirect URI
    # for your API project in the Google API Console.
    app.run('localhost', 8080, debug=True)
