import sqlalchemy
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session

SqlAlchemyBase = orm.declarative_base()

__factory = None


def global_init(db_file):
    global __factory
    if __factory:
        return None
    if not db_file or not db_file.strip():
        raise Exception("Database filename is required")
    conn_str = f"sqlite:///{db_file.strip()}?check_same_thread=False"
    print(f"Successfully connected to database {db_file}")
    engine = sqlalchemy.create_engine(conn_str, echo=False)
    __factory = orm.sessionmaker(bind=engine)

    from . import __all_models

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()
