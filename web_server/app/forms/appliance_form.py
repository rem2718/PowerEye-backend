from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired

class ApplianceForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    type = SelectField('Type', choices=[('type1', 'Type 1'), ('type2', 'Type 2')], validators=[DataRequired()])
    choose_plug = SelectField('Choose Plug', choices=[('plug1', 'Plug 1'), ('plug2', 'Plug 2')], validators=[DataRequired()])
    submit = SubmitField('Add Appliance')
