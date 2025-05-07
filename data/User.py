from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase
from flask_login import UserMixin
import sqlalchemy


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = "user"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    email = sqlalchemy.Column(sqlalchemy.String, nullable=False, index=True, unique=True)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    gender = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("gender.id"), nullable=False)
    goal = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("goal.id"), nullable=True, default=2)
    lifestyle = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("lifestyle.id"), nullable=True, default=3)

    age = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    weight = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    height = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)

    is_admin = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=False)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    gender_obj = sqlalchemy.orm.relationship("Gender")
    goal_obj = sqlalchemy.orm.relationship("Goal")
    lifestyle_obj = sqlalchemy.orm.relationship("Lifestyle")

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
