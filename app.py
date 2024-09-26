from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Replace with a secure key in production

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Modify the users dictionary to store hashed passwords
users = {
    'admin': {
        'password': generate_password_hash('password123')
    }
}

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@app.context_processor
def inject_now():
    return {'current_year': datetime.utcnow().year}


@login_manager.user_loader
def load_user(user_id):
    if user_id in users:
        return User(user_id)
    return None

# Login Form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/merch')
def merch():
    return render_template('merch.html')

@app.route('/social-links')
def social_links():
    return render_template('social_links.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = users.get(username)
        if user and check_password_hash(user['password'], password):
            user_obj = User(username)
            login_user(user_obj)
            return redirect(url_for('hub'))
        else:
            flash('Invalid credentials. Please try again.')
    return render_template('login.html', form=form)


@app.route('/hub')
@login_required
def hub():
    return render_template('hub.html')

@app.route('/manage-links', methods=['GET', 'POST'])
@login_required
def manage_links():
    # Implement link management logic here
    return render_template('manage_links.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
