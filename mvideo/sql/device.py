from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from base import Base


class Device(Base):
    __tablename__ = "device"

    product_id = Column(Integer, primary_key=True)
    name = Column(String)
    url = Column(String)
    brand = Column(String)
    image_url = Column(String)
    # category = Column(ForeignKey('category.category_id'))

    device_categories = relationship(
                            "Category",
                            secondary="cat_dev_assoc",
                            back_populates="devices",
                            # cascade="all"
                            )

    def __init__(self, product_id: int, name: str = "", url: str = "", brand: str = "", image_url: str = "", categories: list = []):
        self.product_id = int(product_id)
        self.name = name
        self.url = url
        self.brand = brand
        self.image_url = image_url
        self.categories = []
        for cat in categories:
            self.device_categories.append(int(cat))  # = Category(int(cat["id"]), str(cat["name"]))

    def __str__(self):
        return f"{self.name} ({self.product_id})"
