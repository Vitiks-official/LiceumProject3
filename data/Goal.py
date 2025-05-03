from .db_session import SqlAlchemyBase
import sqlalchemy


class Goal(SqlAlchemyBase):
    __tablename__ = "goal"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    goal = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    coefficient = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
