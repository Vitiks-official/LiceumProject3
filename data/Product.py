from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase
import sqlalchemy


class Product(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "product"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    calories = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    proteins = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    fats = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    carbohydrates = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
