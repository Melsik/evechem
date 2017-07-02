import os
import base64
import pytz
from datetime import datetime, timedelta

from flask_login import UserMixin
from evechem import db, login_manager
from .types import UTCDateTime

def new_token():
    token = os.urandom(32)
    encoded_token = token.hex()
    return encoded_token

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.String, primary_key=True)
    session_token = db.Column(db.String)
    created_on = db.Column(UTCDateTime(timezone=True))
    session_created_on = db.Column(UTCDateTime(timezone=True))
    session_expires_on = db.Column(UTCDateTime(timezone=True))
    active_character_id = db.Column(db.Integer, db.ForeignKey('characters.id'))

    active_character = db.relationship('Character', foreign_keys=[active_character_id])

    operations = db.relationship('UserOperation')
    merge_requests = db.relationship('AccountMergeRequest', 
        secondary='characters',
        primaryjoin='User.id==Character.user_id',
        secondaryjoin='Character.id==AccountMergeRequest.sending_character_id')

    incomming_requests = db.relationship('AccountMergeRequest',
        secondary='characters',
        primaryjoin='User.id==Character.user_id',
        secondaryjoin='Character.id==AccountMergeRequest.receiving_character_id')

    def get_id(self):
        return str(self.session_token)

    def new_session(self, duration=None):
        self.session_token = new_token()
        now = datetime.now(pytz.utc)
        if duration is None:
            expires = now + timedelta(days=100000) # hack?
        else:
            expires = now + timedelta(seconds=duration)

        self.session_created_on = now
        self.session_expires_on = expires
        return self.session_token


class Character(db.Model):
    __tablename__ = 'characters'

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'))
    name = db.Column(db.String)
    ownerhash = db.Column(db.String)
    scopes = db.Column(db.String)

    auth = db.relationship('Auth', uselist=False)
    user = db.relationship('User', foreign_keys=[user_id], uselist=False,
        backref=db.backref('characters', lazy='dynamic'))


class Key(db.Model):
    __tablename__ = 'keys'

    key = db.Column(db.String, primary_key=True)
    operation_id = db.Column(db.Integer, db.ForeignKey('operations.id'))
    user_id = db.Column(db.String, db.ForeignKey('users.id'))
    access = db.Column(db.String)

    operation = db.relationship('Operation')
    user = db.relationship('User')

class UserOperation(db.Model):
    '''Links users with operations.  The relationship
    is defined by what keys are assigned to what users,
    and what operations those keys can access.'''
    __tablename__ = 'user_operations'

    user_id = db.Column(db.String, db.ForeignKey('users.id'), primary_key=True)
    operation_id = db.Column(db.Integer, db.ForeignKey('operations.id'), primary_key=True)
    key = db.Column(db.String, db.ForeignKey('keys.key'))
    access = db.Column(db.String)

    user = db.relationship('User')
    operation = db.relationship('Operation')


t_user_characters = db.Table('user_characters',
    db.Column('user', db.Integer, db.ForeignKey('users.id')),
    db.Column('character', db.Integer, db.ForeignKey('characters.id'))
    )

class Operation(db.Model):
    __tablename__ = 'operations'

    id = db.Column(db.Integer, primary_key=True)

    masterkey = db.relationship('Key', primaryjoin='and_(Key.operation_id==Operation.id,Key.access=="master")')
    keys = db.relationship('Key')
    users = db.relationship('UserOperation')


class Auth(db.Model):
    __tablename__ = 'auth'

    character_id = db.Column(db.BigInteger, db.ForeignKey('characters.id'), primary_key=True)
    access_token = db.Column(db.String)
    expires_in = db.Column(db.Integer)
    expires_on = db.Column(UTCDateTime(timezone=True))
    refresh_token = db.Column(db.String)
    token_type = db.Column(db.String)

    character = db.relationship('Character', uselist=False)



t_toggle_settings = db.Table('toggle_settings',
    db.Column('user', db.Integer, db.ForeignKey('users.id')),
    db.Column('id', db.Integer),
    db.Column('value', db.Boolean)
    )

class AccountMergeRequest(db.Model):
    '''Merge Request
    Created when a user sends a request for a character to be 
    merged into their account.  The account that owns the 
    requested character must log in and accept or deny the request.

    Status Codes

    :"pending"
    Default status code, set when request is created

    :"denied"
    Status code set when the target user explicitly denies the 
    merge request

    :"accepted"
    Status code set when the target user explicitly accepts the 
    merge request. Note the request is never deleted, only updated.
    '''


    __tablename__ = 'merge_requests'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    created_on = db.Column(UTCDateTime(timezone=True))
    sending_character_id = db.Column(db.BigInteger, db.ForeignKey('characters.id'))
    receiving_character_id = db.Column(db.BigInteger, db.ForeignKey('characters.id'), primary_key=True)
    status = db.Column(db.String, default='pending')
    ignored = db.Column(db.Boolean, default=False)

    user = db.relationship('User', uselist=False)
    sending_character = db.relationship('Character', foreign_keys=[sending_character_id])
    receiving_character = db.relationship('Character', foreign_keys=[receiving_character_id])


@login_manager.user_loader
def load_user(session_token):
    return User.query.filter_by(session_token=session_token).first()
