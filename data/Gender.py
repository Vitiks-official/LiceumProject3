from .db_session import SqlAlchemyBase
import sqlalchemy


class Gender(SqlAlchemyBase):
    __tablename__ = "gender"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    gender = sqlalchemy.Column(sqlalchemy.String, nullable=False)

