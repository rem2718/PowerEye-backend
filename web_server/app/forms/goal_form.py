from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import DataRequired

class GoalForm(FlaskForm):
    energy_goal = IntegerField('Energy Goal', validators=[DataRequired()])
    submit = SubmitField('Set Goal')
