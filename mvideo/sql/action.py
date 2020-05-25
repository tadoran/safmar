from sqlalchemy import Column, String, Integer
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from sql.base import Base
from sql.repr_mixin import ReprMixin


class Action(ReprMixin, Base):
    __tablename__ = "action"

    id = Column(Integer().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)

    # device_actions = relationship(
    #     "DeviceAction",
    #     back_populates="action",
    #     cascade="all"
    # )

    def __init__(self, name: str):
        self.name = name
