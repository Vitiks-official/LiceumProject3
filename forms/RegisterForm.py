from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, NumberRange


class RegisterForm(FlaskForm):
    email = EmailField("Электронная почта", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    name = StringField("Имя", validators=[DataRequired()])
    surname = StringField("Фамилия", validators=[DataRequired()])

    age = IntegerField("Возраст", validators=[DataRequired(), NumberRange(min=5, max=200,
                                                                          message="Возраст - число от 5 до 200!")])
    weight = IntegerField("Вес", validators=[DataRequired(), NumberRange(min=10, max=600,
                                                                         message="Вес - число от 10 до 600!")])
    height = IntegerField("Рост", validators=[DataRequired(), NumberRange(min=50, max=300,
                                                                          message="Рост - число от 50 до 300!")])
    gender = SelectField("Пол", choices=[(1, "Мужской"), (2, "Женский")])

    submit = SubmitField("Готово")
