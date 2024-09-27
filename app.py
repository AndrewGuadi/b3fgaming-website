# app.py

from flask import Flask, render_template, redirect, url_for, request, flash, abort
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Platform, SocialLink
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
import threading

from forms import LoginForm, SocialLinkForm  # Importing the forms from forms.py

app = Flask(__name__)

# Configure Flask app
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_default_secret_key')  # Use environment variable in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///b3fgaming.db'  # Replace with your DB URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure upload folder and allowed extensions (if using image uploads for custom icons)
UPLOAD_FOLDER = 'static/images/social_icons/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.login_view = 'login'  # Specifies the login route
login_manager.init_app(app)

# Flag to ensure setup runs only once
app_has_run_before = False
setup_lock = threading.Lock()


def allowed_file(filename):
    """
    Check if the uploaded file has an allowed extension.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@login_manager.user_loader
def load_user(user_id):
    """
    User loader callback for Flask-Login.
    """
    return User.query.get(int(user_id))


@app.before_request
def before_request():
    """
    Ensure setup tasks run only once before the first request.
    """
    global app_has_run_before
    if not app_has_run_before:
        with setup_lock:
            if not app_has_run_before:
                create_default_user()
                app_has_run_before = True


def create_default_user():
    """
    Create a default user named 'bout3fiddy' with password 'cudderfish123' if it doesn't exist.
    """
    default_username = 'bout3fiddy'
    default_password = 'cudderfish123'
    user = User.query.filter_by(username=default_username).first()
    if not user:
        hashed_password = generate_password_hash(default_password)
        new_user = User(username=default_username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        print(f"Default user '{default_username}' created with password '{default_password}'.")


# Public Routes

@app.route('/')
def home():
    """
    Home page route.
    """
    return render_template('home.html')


@app.route('/social_links')
def social_links():
    """
    Social Links public page. Accessible to everyone.
    """
    social_links = SocialLink.query.all()
    return render_template('social_links.html', social_links=social_links)


@app.route('/merch')
def merch():
    """
    Merch page route.
    """
    return render_template('merch.html')  # Corrected from render_templates


# Protected Routes

@app.route('/hub')
@login_required
def hub():
    """
    Hub page route. Accessible only to logged-in users.
    """
    return render_template('hub.html')


@app.route('/manage_social_links', methods=['GET', 'POST'])
@login_required
def manage_social_links():
    """
    Manage Social Links route. Allows the authenticated user to add new social links.
    """
    form = SocialLinkForm()
    if form.validate_on_submit():
        platform_id = form.platform_id.data
        platform_custom = form.platform_custom.data.strip()
        url = form.url.data.strip()

        if platform_id != 0:  # 0 indicates 'Custom'
            platform = Platform.query.get(platform_id)
            if not platform:
                flash('Selected platform does not exist.', 'danger')
                return redirect(url_for('manage_social_links'))
            platform_name = platform.name
        else:  # platform_id == 0 indicates 'Custom'
            if not platform_custom:
                flash('Custom platform name is required.', 'danger')
                return redirect(url_for('manage_social_links'))
            platform_name = platform_custom

        # Check for duplicate social link
        if platform_id != 0:
            existing_link = SocialLink.query.filter_by(user_id=current_user.id, platform_id=platform_id).first()
        else:
            existing_link = SocialLink.query.filter_by(user_id=current_user.id, platform_custom=platform_name).first()

        if existing_link:
            flash('This social link already exists.', 'warning')
            return redirect(url_for('manage_social_links'))

        # Handle custom icon upload if needed (optional)
        # Currently, custom platforms do not have icons

        new_link = SocialLink(
            platform_id=platform_id if platform_id != 0 else None,
            platform_custom=platform_name if platform_id == 0 else None,
            url=url,
            user_id=current_user.id
        )
        db.session.add(new_link)
        db.session.commit()
        flash('Social link added successfully!', 'success')
        return redirect(url_for('manage_social_links'))

    # Retrieve existing social links for the current user
    social_links = SocialLink.query.filter_by(user_id=current_user.id).all()
    platforms = Platform.query.all()

    return render_template('manage_social_links.html', social_links=social_links, platforms=platforms, form=form)


@app.route('/edit_social_link/<int:link_id>', methods=['GET', 'POST'])
@login_required
def edit_social_link(link_id):
    """
    Edit Social Link route. Allows the authenticated user to edit their existing social links.
    """
    link = SocialLink.query.get_or_404(link_id)
    if link.user_id != current_user.id:
        flash('You do not have permission to edit this link.', 'danger')
        return redirect(url_for('manage_social_links'))

    form = SocialLinkForm(obj=link)

    if form.validate_on_submit():
        platform_id = form.platform_id.data
        platform_custom = form.platform_custom.data.strip()
        url = form.url.data.strip()

        if platform_id != 0:
            platform = Platform.query.get(platform_id)
            if not platform:
                flash('Selected platform does not exist.', 'danger')
                return redirect(url_for('edit_social_link', link_id=link_id))
            platform_name = platform.name
            link.platform_id = platform_id
            link.platform_custom = None
        else:
            if not platform_custom:
                flash('Custom platform name is required.', 'danger')
                return redirect(url_for('edit_social_link', link_id=link_id))
            platform_name = platform_custom
            link.platform_id = None
            link.platform_custom = platform_name

        # Check for duplicate if platform or custom platform has changed
        if platform_id != 0:
            existing_link = SocialLink.query.filter_by(user_id=current_user.id, platform_id=platform_id).first()
        else:
            existing_link = SocialLink.query.filter_by(user_id=current_user.id, platform_custom=platform_name).first()

        if existing_link and existing_link.id != link.id:
            flash('This social link already exists.', 'warning')
            return redirect(url_for('edit_social_link', link_id=link.id))

        link.url = url
        db.session.commit()
        flash('Social link updated successfully!', 'success')
        return redirect(url_for('manage_social_links'))

    return render_template('edit_social_link.html', form=form, link=link)


@app.route('/delete_social_link/<int:link_id>', methods=['POST'])
@login_required
def delete_social_link(link_id):
    """
    Delete Social Link route. Allows the authenticated user to delete their existing social links.
    """
    link = SocialLink.query.get_or_404(link_id)
    if link.user_id != current_user.id:
        flash('You do not have permission to delete this link.', 'danger')
        return redirect(url_for('manage_social_links'))

    db.session.delete(link)
    db.session.commit()
    flash('Social link deleted successfully!', 'success')
    return redirect(url_for('manage_social_links'))


# Authentication Routes

@app.route('/login', methods=['GET', 'POST'])
# @limiter.limit("5 per minute")  # Limit login attempts (Disabled as per your request)
def login():
    """
    Login route. Handles user authentication.
    """
    form = LoginForm()  # Instantiate the form
    if form.validate_on_submit():  # Handle form submission
        username = form.username.data
        password = form.password.data  # Password entered by the user

        # Lookup user by username
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):  # Verify password
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html', form=form)  # Pass the form to the template


@app.route('/logout')
@login_required
def logout():
    """
    Logout route. Logs out the current user.
    """
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

# Removed the /register route to disable user registration

if __name__ == '__main__':
    app.run(debug=True)
def create_default_user():
    """
    Create a default user named 'bout3fiddy' with password 'cudderfish123' if it doesn't exist.
    """
    default_username = 'bout3fiddy'
    default_password = 'cudderfish123'
    user = User.query.filter_by(username=default_username).first()
    if not user:
        hashed_password = generate_password_hash(default_password)
        new_user = User(username=default_username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        print(f"Default user '{default_username}' created with password '{default_password}'.")

def populate_default_social_links():
    """
    Populate the default user with initial social links: YouTube, Twitch, and Instagram.
    """
    default_username = 'bout3fiddy'
    user = User.query.filter_by(username=default_username).first()
    if not user:
        print(f"User '{default_username}' does not exist. Cannot populate social links.")
        return

    # Define the initial social links
    initial_links = [
        {
            'platform_name': 'YouTube',
            'url': 'https://www.youtube.com/c/bout3fiddy'
        },
        {
            'platform_name': 'Twitch',
            'url': 'https://www.twitch.tv/bout3fiddy'
        },
        {
            'platform_name': 'Instagram',
            'url': 'https://www.instagram.com/bout3fiddy'
        }
    ]

    for link in initial_links:
        platform = Platform.query.filter_by(name=link['platform_name']).first()
        if not platform:
            print(f"Platform '{link['platform_name']}' does not exist. Skipping this link.")
            continue

        # Check if the social link already exists for the user
        existing_link = SocialLink.query.filter_by(user_id=user.id, platform_id=platform.id).first()
        if existing_link:
            print(f"Social link for platform '{platform.name}' already exists for user '{user.username}'. Skipping.")
            continue

        # Create and add the new social link
        new_social_link = SocialLink(
            platform_id=platform.id,
            platform_custom=None,
            url=link['url'],
            user_id=user.id
        )
        db.session.add(new_social_link)
        print(f"Added social link for platform '{platform.name}' to user '{user.username}'.")

    db.session.commit()
    print("Default social links populated successfully.")
