from sqlalchemy import Column, String

from app import db


class Service(db.Model):
    __tablename__ = 'service'

    id = Column(String, unique=True)
    code = Column('code', String(512), unique=True)
