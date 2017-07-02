from datetime import datetime, timedelta
import requests
import pytz
import base64

from flask import Flask, session
from flask_oauthlib.client import OAuth
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user

login_manager = LoginManager()
db = SQLAlchemy()


def make_app():
    app = Flask(__name__, instance_relative_config=True, instance_path='/srv/evechem/appdata/instance')
    app.config.from_object('config.default')
    app.config.from_pyfile('config.py') # instance configuration
    db.init_app(app)
    login_manager.init_app(app)

    return app

app = make_app()


ssoconfig = app.config.get_namespace('EVESSO_', lowercase=False)
oauth = OAuth()
eve_api = oauth.remote_app('EVEOAUTH',
    consumer_key=ssoconfig['CLIENT_KEY'],
    consumer_secret=ssoconfig['CLIENT_SECRET'],
    base_url=ssoconfig['API_URL'],
    access_token_url=ssoconfig['TOKEN_URL'],
    authorize_url=ssoconfig['AUTH_URL'],
    access_token_method=ssoconfig['ACCESS_TOKEN_METHOD'],
    request_token_method=ssoconfig['REQUEST_TOKEN_METHOD'],
    request_token_params={'scope':ssoconfig['SCOPES']})


@eve_api.tokengetter
def get_eve_api_oauth_token(token='access'):
    # return access token

    if token == 'access':
        if current_user.is_authenticated:
            character = current_user.active_character
            if character.auth.expires_on <= datetime.now(pytz.utc):
                # if the token has expired, refresh it
                resp = refresh_token()

                character.auth.access_token = resp['access_token']
                character.auth.expires_in = resp['expires_in']
                expires_on = datetime.now(pytz.utc) + timedelta(seconds=resp['expires_in'])
                character.auth.expires_on = expires_on
                character.auth.token_type = resp['token_type']
                db.session.commit()

                session['evesso_token'] = (resp['access_token'], '')
                return resp['access_token'], ''

            else:
                # otherwise return the EVE SSO access token
                return character.auth.access_token, ''
        else:
            # to get around when the access token is needed, 
            # but not bound to a character yet
            return session['evesso_token']

    elif token == 'refresh':
        # return the refresh token
        character = current_user.active_character
        return character.auth.refresh_token, ''

def refresh_token():
    auth_hash = base64.b64encode(bytes(eve_api.consumer_key + ':' + eve_api.consumer_secret,'utf-8'))
    auth_header = b'Basic %s' % auth_hash
    headers = {
        'Authorization': auth_header,
        'Host': 'login.eveonline.com',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    request_data = {
        'grant_type':'refresh_token',
        'refresh_token':get_eve_api_oauth_token('refresh')[0]
    }
    resp = requests.post(
        url=app.config['EVESSO_TOKEN_URL'],
        data=request_data,
        headers=headers)

    return resp.json()


import evechem.models
import evechem.views

# build the database
with app.app_context():
    db.create_all()
    db.session.commit()
