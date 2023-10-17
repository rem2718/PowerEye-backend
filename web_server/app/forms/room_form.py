from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FieldList
from wtforms.validators import DataRequired, Length

class RoomForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    devices = FieldList(StringField('Device'), min_entries=2, validators=[Length(min=2, message='At least 2 devices are required.')])
    submit = SubmitField('Create Room')
