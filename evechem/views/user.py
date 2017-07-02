import pytz
from datetime import datetime, timedelta

from flask import render_template, url_for, session, redirect, request
from flask_login import login_required, login_user, logout_user, current_user

from evechem import app, eve_api, db
from evechem.models.user import User, Character, Auth, AccountMergeRequest


@app.route('/user/add-character', methods=['POST'])
@login_required
def charadd_request():
    recv_char_id = int(request.form['character'])

    sending_char = current_user.active_character

    merge_request = AccountMergeRequest(
        user_id=current_user.id,
        created_on=datetime.now(pytz.utc),
        sending_character_id=sending_char.id,
        receiving_character_id=recv_char_id
        )

    db.session.add(merge_request)
    db.session.commit()

    return redirect(url_for('user_page'))