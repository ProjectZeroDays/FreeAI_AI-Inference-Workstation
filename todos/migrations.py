from sqlalchemy import create_engine


def create_tables(engine):
    from todos.models import Base
    Base.metadata.create_all(bind=engine)
