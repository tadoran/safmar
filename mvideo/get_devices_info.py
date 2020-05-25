import asyncio

from aiohttp import ClientSession

from graphql.device_details import GraphqlDeviceDetails
from graphql_get_async import get_devices_info
from sql.base import Session, engine, Base
from sql.category import Category
from sql.device import Device
from sql.brand import Brand


async def get_devices_details(devices: list = []):
    async with ClientSession() as aio_session:
        result = await get_devices_info(devices=devices,
                                        session=aio_session,
                                        graphql_classes=[GraphqlDeviceDetails]
                                        )
    return result


def get_devices_information(session):
    devs = (session
            .query(Device.product_id)
            .filter(Device.name == "")
            # .join(Device.device_categories)
            # .join(Category.tasks)
            # .filter(Task.name == "Test")
            .all()
            )
    devs_list = [t.product_id for t in devs]

    brands = session.query(Brand).all()
    brands_hash = {b.name: b for b in brands}

    if len(devs_list) == 0:
        print(f"There are no articles without description in DB.")
    else:
        print(f"There are {len(devs_list)} articles with no description in DB.")

        base_url = "https://www.mvideo.ru/products/"
        chunksize = 400
        ran = list(range(0, len(devs_list) + 1, chunksize))
        details_chunks = (devs_list[i:i + chunksize] for i in ran)
        for n, chunk in enumerate(details_chunks):
            details = asyncio.run(get_devices_details(chunk))
            for article, dev_details in details.items():
                if len(dev_details) == 0: continue

                if dev_details.get("brand", None) in brands_hash:
                    brand = brands_hash[dev_details["brand"]]
                else:
                    brand_name = dev_details.get("brand", None)
                    if brand_name is None:
                        continue
                    brand = session.merge(Brand(brand_name))
                    session.commit()
                    brands_hash[dev_details["brand"]] = brand

                device = Device(
                    product_id=int(article),
                    name=dev_details.get("desr", None),
                    url=base_url + dev_details.get("link", None),
                    brand= brand.id,
                    image_url=dev_details.get("imgUrl", None)
                )
                session.merge(device)
            session.commit()
            print(f"Chunk #{n} has been processed.")
        print(f"All descriptions were updated.")


if __name__ == "__main__":
    session = Session(bind=engine)
    Base.metadata.create_all(bind=engine)

    get_devices_information(session)
