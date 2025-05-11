from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, FloatField, BooleanField
from wtforms.validators import DataRequired, NumberRange


# Form for adding new product to the database
class AddProductForm(FlaskForm):
    product = StringField("Название продукта", validators=[DataRequired()])
    calories = FloatField("Калории", validators=[DataRequired(), NumberRange(min=0, max=999)])
    proteins = FloatField("Белки, г", validators=[DataRequired(), NumberRange(min=0, max=999)])
    fats = FloatField("Жиры, г", validators=[DataRequired(), NumberRange(min=0, max=999)])
    carbohydrates = FloatField("Углеводы, г", validators=[DataRequired(), NumberRange(min=0, max=999)])
    is_public = BooleanField("Открыть другим пользователям")
    submit = SubmitField("Готово")
