from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FileField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class ProfileEditForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    meross_password = PasswordField('Meross Password', validators=[DataRequired(), Length(min=6)])
    profile_pic = FileField('Profile Picture')
    submit = SubmitField('Save Changes')
