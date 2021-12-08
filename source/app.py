import os
import flask
import pickle
import json

import google_auth_oauthlib.flow

from flask import request
from flask_cors import CORS, cross_origin

from task_mgr import TaskMgr, data_sync_task, analyze_data_task
from mongo_client import MongoDBClient
from logger import logger

# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
CLIENT_SECRETS_FILE = "client_secret.json"

# token file.
ACCESS_TOKEN_FILE = "token.pickle"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.send',
          'https://www.googleapis.com/auth/gmail.labels']

API_SERVICE_NAME = 'gmail'
API_VERSION = 'v1'

app = flask.Flask(__name__, static_folder='./webapp/build', static_url_path='/')
# Note: A secret key is included in the sample so that it works.
# If you use this code in your application, replace this with a truly secret
# key. See https://flask.palletsprojects.com/quickstart/#sessions.
app.secret_key = 'REPLACE ME - this value is here as a placeholder.'
CORS(app)

task_manager = TaskMgr()
mdb_client = MongoDBClient()


@app.route('/')
def index():
    if not os.path.exists(ACCESS_TOKEN_FILE):
        return flask.redirect("/authorize")
    return app.send_static_file("index.html")


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

    # TODO: use redirect
    # return app.send_static_file("index.html")
    return flask.redirect("/")


@app.route('/clear')
def clear_credentials():
    if 'credentials' in flask.session:
        del flask.session['credentials']
    return ('Credentials have been cleared.<br><br>' +
            index())


@app.route('/data-sync')
@cross_origin()
def data_sync():
    mdb_client.get_db_handle().sync_status.update_one(
        {'_id': 1},
        {
            '$set': {
                'sync_status': "pending",
            }
        },
        upsert=True
    )
    task_manager.execute_task(data_sync_task)
    return 'Successfully started a task to sync emails from Gmail.'


@app.route('/data-sync-status')
@cross_origin()
def data_sync_status():
    sync_status = mdb_client.get_sync_status()
    return json.dumps(sync_status)


@app.route('/analyze-emails')
@cross_origin()
def analyze_emails():
    mdb_client.get_db_handle().analyze_status.update_one(
        {'_id': 1},
        {
            '$set': {
                'analyze_status': "pending",
            }
        },
        upsert=True
    )
    task_manager.execute_task(analyze_data_task)
    return 'Successfully started a task to sync emails from Gmail.'


@app.route('/analyze-status')
@cross_origin()
def analyze_status():
    db_analyze_status = mdb_client.get_analyze_status()
    return json.dumps(db_analyze_status)


@app.route('/topic-summary')
@cross_origin()
def get_topic_summary():
    # replace with actual topics from DB
    topics = mdb_client.get_db_handle().topics.find({})
    result = list()
    for topic in topics:
        print(f"searching {topic['topic']}")
        all_cnt, unread_cnt = mdb_client.get_message_counts(topic['topic'])
        keywords = [kw.replace("_", " ") for kw in topic['words']]
        result.append(
            {
                'total': all_cnt,
                'unread': unread_cnt,
                'topic': topic['topic'],
                'keywords': keywords
            }
        )
    return json.dumps(result)


@app.route('/emails')
@cross_origin()
def get_emails():
    topic = request.args.get('topic')
    logger.debug(topic)
    emails = mdb_client.get_db_handle().emails.find(
        {
            "topics": {"$all": [topic]}
        },
        {
            "messageId": 1,
            "subject": 1,
            "from": 1,
            "topics": 1
        }
    )
    return json.dumps(list(emails))


def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}


def quick_test():
    print(get_topic_summary())


def reset_running_jobs():
    mdb_h = mdb_client.get_db_handle()

    cur = mdb_h.sync_status.find(
        {'_id': 1}
    )

    if cur.count() == 0:
        # very first time.
        mdb_client.get_db_handle().sync_status.update_one(
            {'_id': 1},
            {
                '$set': {
                    'sync_status': "not synced",
                }
            },
            upsert=True
        )
    else:
        sync_status = cur.next()
        if sync_status.get('sync_status') == 'syncing' or \
                sync_status.get('sync_status') == 'pending':
            mdb_client.get_db_handle().sync_status.update_one(
                {'_id': 1},
                {
                    '$set': {
                        'sync_status': "aborted",
                    }
                },
                upsert=True
            )

    cur = mdb_h.analyze_status.find(
        {'_id': 1}
    )

    if cur.count() == 0:
        # very first time.
        mdb_client.get_db_handle().analyze_status.update_one(
            {'_id': 1},
            {
                '$set': {
                    'analyze_status': "not analyzed",
                }
            },
            upsert=True
        )
    else:
        db_analyze_status = cur.next()
        if db_analyze_status.get('analyze_status') == 'analyzing' or \
                db_analyze_status.get('analyze_status') == 'pending':
            mdb_h.analyze_status.update_one(
                {'_id': 1},
                {
                    '$set': {
                        'analyze_status': "aborted",
                    }
                },
                upsert=True
            )


if __name__ == '__main__':
    # When running locally, disable OAuthlib's HTTPs verification.
    # ACTION ITEM for developers:
    #     When running in production *do not* leave this option enabled.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    # Specify a hostname and port that are set as a valid redirect URI
    # for your API project in the Google API Console.
    reset_running_jobs()
    app.run('0.0.0.0', 8080, debug=True)
