from sql.base import Session, engine, Base
from sql.task import Task
from sql.category import Category
from sql.device import Device
from sql.price import Price

from graphql_get_async import get_devices_info
from graphql.device_details import GraphqlDeviceDetails

import asyncio
from aiohttp import ClientSession


async def get_devices_details(devices: list = []):
    async with ClientSession() as aio_session:
        result = await get_devices_info(devices=devices,
                                        session=aio_session,
                                        graphql_classes=[GraphqlDeviceDetails]
                                        )
    return result

session = Session(bind=engine)
Base.metadata.create_all(bind=engine)

devs = (session
               .query(Device.product_id)
               .filter(Device.name == "")
               .join(Device.device_categories)
               .join(Category.tasks)
               # .filter(Task.name == "Test")
               .all()
        )
devs_list = [t.product_id for t in devs]
print(devs_list)
print(len(devs_list))

base_url = "https://www.mvideo.ru/products/"
chunksize = 400
ran = list(range(0, len(devs_list)+1, chunksize))
details_chunks = (devs_list[i:i+chunksize] for i in ran)
for chunk in details_chunks:
    details = asyncio.run(get_devices_details(chunk))
    for article, dev_details in details.items():
        if len(dev_details) == 0: continue
        device = Device(
            product_id=int(article),
            name=dev_details.get("desr", None),
            url=base_url + dev_details.get("link", None),
            brand=dev_details.get("brand", None),
            image_url=dev_details.get("imgUrl", None)
        )
        session.merge(device)
    session.commit()
    print(chunk)

