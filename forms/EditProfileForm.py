from flask_wtf import FlaskForm
from wtforms import FileField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional


class EditProfileForm(FlaskForm):
    avatar = FileField("Загрузить новый аватар")

    goal = SelectField("Ваша цель", choices=[
        (1, "Сбросить вес"),
        (2, "Поддерживать вес"),
        (3, "Набрать вес")
    ], validators=[DataRequired()])

    lifestyle = SelectField("Образ жизни", choices=[
        (1, "Сидячий образ жизни"),
        (2, "Низкая активность"),
        (3, "Умеренная активность"),
        (4, "Высокая активность"),
        (5, "Очень высокая активность")
    ])

    height = IntegerField("Рост, см", validators=[Optional(), NumberRange(min=50, max=300,
                                                                          message="Рост - число от 50 до 300!")])
    weight = IntegerField("Вес, кг", validators=[Optional(), NumberRange(min=10, max=600,
                                                                         message="Вес - число от 10 до 600!")])
    age = IntegerField("Возраст", validators=[Optional(), NumberRange(min=5, max=200,
                                                                      message="Возраст - число от 5 до 200!")])
    submit = SubmitField("Сохранить изменения")