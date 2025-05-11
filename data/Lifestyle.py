from .db_session import SqlAlchemyBase
import sqlalchemy


# Database model for lifestyles
class Lifestyle(SqlAlchemyBase):
    __tablename__ = "lifestyle"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    lifestyle = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    coefficient = sqlalchemy.Column(sqlalchemy.Float, nullable=False)


