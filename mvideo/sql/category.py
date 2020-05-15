from sqlalchemy import Column, String, Integer
from sqlalchemy import Table, ForeignKey

from sqlalchemy.orm import relationship

from base import Base


category_device_association = Table('cat_dev_assoc', Base.metadata,
                                    Column('category_id', Integer, ForeignKey('category.category_id')),
                                    Column('product_id', Integer, ForeignKey('device.product_id'))
                                    )


class Category(Base):
    __tablename__ = "category"

    category_id = Column(Integer, primary_key=True)
    name = Column(String)

    devices = relationship("Device", secondary="cat_dev_assoc",  back_populates="device_categories")
    tasks   = relationship("Task",   secondary="task_cat_assoc", back_populates="categories")

    def __init__(self, category_id: int, name: str):
        self.category_id = category_id
        self.name = name

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.name}')"

    def __str__(self):
        return f"{self.name} ({self.category_id})"
