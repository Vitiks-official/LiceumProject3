from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase
import sqlalchemy


# Database model for articles
class Article(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "article"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    accepted = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=True)

    user = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("user.id"), nullable=True)
    user_obj = sqlalchemy.orm.relationship("User")
