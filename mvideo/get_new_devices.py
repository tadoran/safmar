import asyncio

from aiohttp import ClientSession

from graphql_get_async import get_category_devices
from sql.base import Session, engine, Base
from sql.category import Category
from sql.device import Device
from sql.task import Task


async def get_all_category_devices(categories: dict):
    """Get Graphql device-related data
    :param categories - all categories to be requested
    :returns dict of devices in categories ({(category name, category id):[devices...]}"""
    category_tasks = {}
    async with ClientSession() as session:
        for cat_name, cat_id in categories.items():
            category_tasks[(cat_name, cat_id)] = asyncio.create_task(get_category_devices(cat_id, session))
        await asyncio.gather(*category_tasks.values())
    return {key: val.result() for key, val in category_tasks.items()}


def get_new_devices(session):
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

    # All devices which are already in DB
    db_devices = [el.product_id for el in session.query(Device).all()]
    new_devices = []

    all_categories = {key: val for t in categories for key, val in categories[t].items()}
    devices = asyncio.run(get_all_category_devices(all_categories))
    for (cat_name, cat_key), cat_devices in devices.items():
        for device in cat_devices:
            if int(device) not in db_devices:
                dev = Device(product_id=int(device))
                dev.device_categories.append(session.merge(Category(cat_key, cat_name)))
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


if __name__ == "__main__":
    session = Session(bind=engine)
    Base.metadata.create_all(bind=engine)

    get_new_devices(session)
