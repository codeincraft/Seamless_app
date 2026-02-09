import sqlalchemy as sqlalchemy
import sqlalchemy.ext.declarative as declarative
import sqlalchemy.orm as orm
import os

# DB_URL = "sqlite:///./dbfile.db"
# engine = sqlalchemy.create_engine(DB_URL, connect_args={"check_same_thread": False})
# DB_URL = "postgresql://dbuser:password@localhost/dbname"

# # DB_URL = "mysql://dbuser:password@localhost/dbname"
# engine = sqlalchemy.create_engine(DB_URL)

# SessionLocal = orm.sessionmaker(autocommit = False, autoflush=False, bind=engine)
# Base = declarative.declarative_base()



DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = sqlalchemy.create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = orm.sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative.declarative_base()
