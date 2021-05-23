from sqlalchemy import Column, Integer, String, Boolean, Numeric
from app import db


class Service(db.Model):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    title = Column('title', String(32))
    in_stock = Column('in_stock', Boolean)
    quantity = Column('quantity', Integer)
    price = Column('price', Numeric)
