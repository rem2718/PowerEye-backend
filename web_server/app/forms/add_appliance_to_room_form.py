from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired

class AddApplianceToRoomForm(FlaskForm):
    appliance_id = SelectField('Appliance', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Add Appliance')
