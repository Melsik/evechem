from flask import render_template, url_for, session, redirect, request
from flask_login import login_required, login_user, logout_user, current_user

from evechem import app, eve_api, db
from evechem.models.user import User, Character, Auth



@app.route('/')
def home():
    return render_template('home.html.j2')

@app.route('/operations')
def operations():
    print(current_user)
    return render_template('page.html.j2', active_page='operations')

@app.route('/towers')
def towers():
    return render_template('page.html.j2', active_page='towers')

@app.route('/inventory')
def inventory():
    return render_template('page.html.j2', active_page='inventory')

@app.route('/statistics')
def statistics():
    return render_template('page.html.j2', active_page='statistics')

@app.route('/market')
def market():
    return render_template('page.html.j2', active_page='market')

@app.route('/fuel-ice')
def fuel_ice():
    return render_template('page.html.j2', active_page='fuel-ice')

@app.route('/user')
def user_page():
    if current_user.is_authenticated:
        return render_template('user.html.j2', active_page='user')
    else:
        return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')



import evechem.views.auth
import evechem.views.user