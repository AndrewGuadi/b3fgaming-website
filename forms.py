# forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, URL, Optional

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(message="Username is required."),
        Length(min=3, max=150, message="Username must be between 3 and 150 characters.")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Password is required.")
    ])
    submit = SubmitField('Login')

class SocialLinkForm(FlaskForm):
    platform_id = SelectField('Platform', coerce=int, choices=[], validators=[Optional()])
    platform_custom = StringField('Custom Platform', validators=[Optional(), Length(max=100)])
    url = StringField('URL', validators=[
        DataRequired(message="URL is required."),
        URL(message="Please enter a valid URL.")
    ])
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(SocialLinkForm, self).__init__(*args, **kwargs)
        from models import Platform
        # Populate platform choices from the database
        self.platform_id.choices = [(platform.id, platform.name) for platform in Platform.query.all()]
        # Append the "Custom" option with a unique integer value, e.g., 0
        self.platform_id.choices.append((0, 'Custom'))
