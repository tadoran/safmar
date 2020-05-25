from sqlalchemy import Column, Integer, Date
from sqlalchemy import ForeignKey
from sqlalchemy.sql.functions import current_date
from sqlalchemy.orm import relationship


from sql.base import Base
from sql.action import Action
from sql.repr_mixin import ReprMixin


class DeviceAction(ReprMixin, Base):
    __tablename__ = "device_action"

    id = Column(Integer().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("device.product_id"), key="product", nullable=False)
    start_date = Column(Date, nullable=False, default=current_date(), key="start_date")
    end_date = Column(Date, nullable=False, default=current_date(), key="end_date")
    action = Column(Integer, ForeignKey("action.id"), key="cur_action", nullable=False)

    action_obj = relationship("Action")

    def __init__(self,
                 product,
                 action: int,
                 start_date: Date = None,
                 end_date: Date = None
                 ):
        self.product_id = product
        self.start_date = start_date
        self.end_date = end_date
        self.action = action
