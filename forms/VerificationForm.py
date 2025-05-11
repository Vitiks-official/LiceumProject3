from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField
from wtforms.validators import DataRequired


# Form for user's email verification during registration
class VerificationForm(FlaskForm):
    verification_code = IntegerField("Код подтверждения", validators=[DataRequired()])
    submit = SubmitField("Готово")
