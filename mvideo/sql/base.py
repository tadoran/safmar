from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# engine = create_engine("sqlite:///:memory:", echo=True)
# engine = create_engine("sqlite:///test_db.db", echo=True)
engine = create_engine("sqlite:///test_db.db", echo=False)
Session = sessionmaker(bind=engine)

Base = declarative_base()

