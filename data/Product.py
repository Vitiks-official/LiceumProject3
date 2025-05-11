from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase
import sqlalchemy


# Database model for products
class Product(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "product"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    calories = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    proteins = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    fats = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    carbohydrates = sqlalchemy.Column(sqlalchemy.Float, nullable=False)

    public = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=True)
    accepted = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=True)

    user = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("user.id"), nullable=True)
    user_obj = sqlalchemy.orm.relationship("User")
