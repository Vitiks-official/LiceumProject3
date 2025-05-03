from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    email = EmailField("Электронная почта", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    name = StringField("Имя", validators=[DataRequired()])
    surname = StringField("Фамилия", validators=[DataRequired()])

    age = IntegerField("Возраст", validators=[DataRequired()])
    weight = IntegerField("Вес", validators=[DataRequired()])
    height = IntegerField("Рост", validators=[DataRequired()])
    gender = SelectField("Пол", choices=["Мужской", "Женский"])

    submit = SubmitField("Готово")
