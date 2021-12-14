from datetime import datetime

from flask import Blueprint, render_template, flash
from werkzeug.security import check_password_hash
from flask_login import login_user

from app import db
from models import User
from users.forms import LoginForm

users_blueprint = Blueprint('users', __name__, template_folder='templates')


# view user login
@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    # Validation check for email and password
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if not user or not check_password_hash(user.password, form.password.data):
            flash('Please check your login details and try again')

        login_user(user)

        user.last_logged_in = user.current_logged_in
        user.current_logged_in = datetime.now()
        db.session.add(user)
        db.session.commit()

        return login()
    return render_template('login.html', form=form)
