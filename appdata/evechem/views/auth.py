import uuid
import pytz
from datetime import datetime, timedelta

from flask import render_template, url_for, session, redirect, request
from flask_login import login_required, login_user, logout_user, current_user

from evechem import app, eve_api, db
from evechem.models.user import User, Character, Auth

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/login')
def login():
    return eve_api.authorize(callback=url_for('sso',
        next=url_for('home') or request.referrer or None,
        _external=True,
        _scheme='https'))

@app.route('/sso/')
def sso():
    if current_user.is_authenticated:
        logout_user()
    resp = eve_api.authorized_response()
    session['evesso_token'] = (resp['access_token'],'')

    # acquire character information
    verify = eve_api.get(app.config['EVESSO_VERIFY_URL'])

    c_id = verify.data['CharacterID']
    ownerhash = verify.data['CharacterOwnerHash']

    character = Character.query.get(c_id)


    if character is None:
        # make new character and user
        character = Character(
            id=c_id,
            ownerhash=ownerhash,
            name=verify.data['CharacterName'],
            scopes=verify.data['Scopes']
            )

        user = User(
            id=uuid.uuid4().hex,
            created_on=datetime.now(pytz.utc),
            active_character_id=character.id
            )

        user.characters.append(character)
        db.session.add(character)
        db.session.add(user)
        user.new_session()

    elif character.ownerhash != ownerhash:
        # character changed owner, make new user and update
        old_user = character.user
        if old_user.active_character_id == character.id:
            old_user.active_character_id = None

        
        user = User(
            id=uuid.uuid4().hex,
            created_on=datetime.now(pytz.utc),
            active_character_id=character.id
            )

        character.ownerhash = ownerhash
        character.user_id = user.id

        db.session.add(user)
        user.new_session()

    else:
        # character found
        character.scopes = verify.data['Scopes']
        user = character.user
        user.active_character_id = character.id
        user.new_session()
    auth = Auth.query.get(c_id)
    expires_on = datetime.now(pytz.utc) + timedelta(seconds=resp['expires_in'])
    if auth is None:
        auth = Auth(
            character_id=c_id,
            access_token=resp['access_token'],
            expires_in=resp['expires_in'],
            expires_on=expires_on,
            refresh_token=resp['refresh_token'],
            token_type=resp['token_type'],
            )

        db.session.add(auth)

    else:
        auth.access_token = resp['access_token']
        auth.expires_in = resp['expires_in']
        auth.expires_on = expires_on
        auth.refresh_token = resp['refresh_token']
        auth.token_type = resp['token_type']

    
    db.session.commit()
    login_success = login_user(user)
    response = redirect(request.args.get('next', url_for('home')))

    return response
