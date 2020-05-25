from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref

from sql.base import Base
from sql.repr_mixin import ReprMixin

from sql.price import Price
from sql.device_action import DeviceAction
from sql.brand import Brand


class Device(ReprMixin, Base):
    __tablename__ = "device"

    product_id = Column(Integer, primary_key=True)
    name = Column(String(255))
    url = Column(String(255))
    brand = Column(Integer, ForeignKey("brand.id"))
    image_url = Column(String(255))

    device_categories = relationship(
        "Category",
        secondary="cat_dev_assoc",
        back_populates="devices",
        # cascade="all"
    )
    prices = relationship("Price")
    actions = relationship("DeviceAction")
    brand_obj = relationship("Brand", back_populates="devices")
    # brand_obj = relationship("Brand", backref = backref("Brand", uselist=False))

    def __init__(self, product_id: int, name: str = "", url: str = "", brand: str = "", image_url: str = "",
                 categories: list = []):
        self.product_id = int(product_id)
        self.name = name
        self.url = url
        self.brand = brand
        self.image_url = image_url
        self.categories = []
        for cat in categories:
            self.device_categories.append(int(cat))
