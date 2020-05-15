from sql.base import Session, engine, Base
from sql.task import Task
from sql.category import Category
from sql.device import Device

from graphql_get_async import get_category_devices

import asyncio
from aiohttp import ClientSession

session = Session(bind=engine)
Base.metadata.create_all(bind=engine)

# Which task should be processed?
tasks = (session
                .query(Task)
                # .filter(Task.name == "Test")
                .all()
         )

# Categories to be processed
categories = {}
for task in tasks:
    cats = task.categories
    categories.update({task.name: {c.name: c.category_id for c in cats}})


async def get_devices(category):
    """Get Graphql device-related data
    :param category - category to be requested
    :returns list of devices in given category"""
    async with ClientSession() as session:
        res = await get_category_devices(category, session)
        return res

# All devices which are already in DB
db_devices = [el.product_id for el in session.query(Device).all()]
new_devices = []
for t in categories:
    for key, val in categories[t].items():
        # Request info about all devices in a given category
        devices = asyncio.run(get_devices(val))

        for i, dev_key in enumerate(devices):
            if int(dev_key) not in db_devices:
                # Appending device to DB
                dev = Device(product_id=int(dev_key))
                dev.device_categories.append(Category(val, key))
                new_devices.append(dev.product_id)
                session.merge(dev)
            else:
                # Device is already in DB
                pass

session.commit()

if len(new_devices) > 0:
    print(f"{len(new_devices)} new devices were put into DB.")
else:
    print(f"No new devices were found.")
session.close()
