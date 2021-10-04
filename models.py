from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String
from db import Base


class Product(Base):
    __tablename__ = 'products'

    product_id = Column(Integer, primary_key=True)
    product_name = Column(String)
    product_quantity = Column(Integer)
    product_price = Column(Integer)
    date_updated = Column(DateTime)

    def __init__(self, product_name, product_quantity, product_price, date_updated=None):
        self.product_name = product_name
        self.product_quantity = product_quantity
        self.product_price = product_price
        self.date_updated = date_updated if date_updated else datetime.now()

    def __repr__(self):
        return f'<Product(product_name={self.product_name} product_quantity={self.product_quantity} product_price={self.product_price} date_updated={self.date_updated}) />'

    def as_dict(self):
        return {
            'product_id': self.product_id,
            'product_name': self.product_name,
            'product_quantity': self.product_quantity,
            'product_price': self.product_price,
            'date_updated': self.date_updated
        }

    def as_tuple(self):
        return (self.product_name, str(self.product_quantity), str(self.product_price), str(self.date_updated))
