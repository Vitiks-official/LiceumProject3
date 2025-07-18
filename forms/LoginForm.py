from flask_wtf import FlaskForm
from wtforms import PasswordField, EmailField, SubmitField
from wtforms.validators import DataRequired


# Form for logging the user in
class LoginForm(FlaskForm):
    email = EmailField("Электронная почта", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])

    submit = SubmitField("Готово")
