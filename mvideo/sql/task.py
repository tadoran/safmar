from sqlalchemy import Column, String, Integer
from sqlalchemy import Table, ForeignKey

from sqlalchemy.orm import relationship

from sql.base import Base
from sql.repr_mixin import ReprMixin

task_category_association = Table('task_cat_assoc', Base.metadata,
                                  Column('task_id', Integer, ForeignKey('task.id')),
                                  Column('category_id', Integer, ForeignKey('category.category_id'))
                                  )


class Task(ReprMixin, Base):
    __tablename__ = "task"

    id = Column(Integer, primary_key=True)
    name = Column(String)

    categories = relationship("Category", secondary="task_cat_assoc",  back_populates="tasks")

    def __init__(self, name):
        self.name = name


    def __str__(self):
        return f"{self.name} ({self.id})"
