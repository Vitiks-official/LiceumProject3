from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, FileField, TextAreaField
from wtforms.validators import DataRequired


# Form for adding new article to the database
class AddArticleForm(FlaskForm):
    title = StringField("Заголовок статьи", validators=[DataRequired()])
    picture = FileField("Изображение для статьи")
    content = TextAreaField("Текст", validators=[DataRequired()])
    submit = SubmitField("Готово")
