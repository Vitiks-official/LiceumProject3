from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase
import sqlalchemy


# Database model for statistics
class Statistics(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "statistics"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("user.id"), nullable=False)
    date = sqlalchemy.Column(sqlalchemy.Date, nullable=False)

    calories = sqlalchemy.Column(sqlalchemy.Numeric(precision=10, scale=1), nullable=False)
    proteins = sqlalchemy.Column(sqlalchemy.Numeric(precision=10, scale=1), nullable=False)
    fats = sqlalchemy.Column(sqlalchemy.Numeric(precision=10, scale=1), nullable=False)
    carbohydrates = sqlalchemy.Column(sqlalchemy.Numeric(precision=10, scale=1), nullable=False)

    user_obj = sqlalchemy.orm.relationship("User")
