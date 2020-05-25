import asyncio

from aiohttp import ClientSession
from sqlalchemy.sql.functions import current_date, max as sql_max

from graphql.actions import GraphqlActions
from graphql_get_async import get_devices_info
from sql.base import Session, engine, Base
from sql.device import Device
from sql.brand import Brand
from sql.category import Category
from sql.task import Task
from sql.action import Action
from sql.device_action import DeviceAction


def get_brands(session):
    q = session.query(Device).join(Device.brand_obj).join(Device.device_categories).filter(Brand.name == "Bosch").limit(20000).all()
    for i, device in enumerate(q, 1):
        print(f"{i}) {device.device_categories[0].name} - {device.name}({device.product_id}), {device.brand_obj.name}, ")
    print()
    print()



if __name__ == "__main__":
    session = Session(bind=engine)
    Base.metadata.create_all(bind=engine)

    get_brands(session)
