from sqlalchemy import Column, String, Integer
from sqlalchemy import Table, ForeignKey
from sqlalchemy.orm import relationship

from sql.base import Base
from sql.repr_mixin import ReprMixin


class Brand(ReprMixin, Base):
    __tablename__ = "brand"

    id = Column(Integer().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    name = Column(String(25))

    devices = relationship("Device", back_populates="brand_obj")

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"{self.name} ({self.id})"
