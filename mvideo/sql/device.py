from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from sql.base import Base

from sql.category import Category
from sql.repr_mixin import ReprMixin

from sql.price import Price

class Device(ReprMixin,Base):
    __tablename__ = "device"

    product_id = Column(Integer, primary_key=True)
    name = Column(String)
    url = Column(String)
    brand = Column(String)
    image_url = Column(String)

    device_categories = relationship(
                            "Category",
                            secondary="cat_dev_assoc",
                            back_populates="devices",
                            # cascade="all"
                            )
    prices = relationship("Price")

    def __init__(self, product_id: int, name: str = "", url: str = "", brand: str = "", image_url: str = "", categories: list = []):
        self.product_id = int(product_id)
        self.name = name
        self.url = url
        self.brand = brand
        self.image_url = image_url
        self.categories = []
        for cat in categories:
            self.device_categories.append(int(cat))


