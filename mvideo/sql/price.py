from sqlalchemy import Column, Integer, Date
from sqlalchemy import ForeignKey
from sqlalchemy.sql.functions import current_date

from sql.base import Base
from sql.repr_mixin import ReprMixin


class Price(ReprMixin, Base):
    __tablename__ = "price"

    id = Column(Integer().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    product = Column(Integer, ForeignKey("device.product_id"), key="product")
    start_date = Column(Date, nullable=False, server_default=current_date(), key="start_date")
    end_date = Column(Date, nullable=False, server_default=current_date(), key="end_date")
    base_price = Column(Integer, nullable=False)
    action_price = Column(Integer)
    economy = Column(Integer)

    def __init__(self,
                 product,
                 base_price: int,
                 start_date: Date = None,
                 end_date: Date = None,
                 action_price: int = 0,
                 economy: int = 0
                 ):
        self.product = product
        self.start_date = start_date
        self.end_date = end_date
        self.base_price = base_price
        self.action_price = action_price
        self.economy = economy
