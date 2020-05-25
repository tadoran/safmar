import asyncio

from aiohttp import ClientSession
from sqlalchemy.sql.functions import current_date, max as sql_max

from graphql.price import GraphqlPrice
from graphql_get_async import get_devices_info
from sql.base import Session, engine, Base
from sql.device import Device
from sql.price import Price


async def get_prices(devices: list) -> dict:
    """Get Graphql prices data
    :param devices - list of devices articles
    :returns dict(article:{'actionPrice':str, 'basePrice':int, 'economy': int}, ...)"""
    async with ClientSession() as session:
        res = await get_devices_info(devices, session, [GraphqlPrice])
        return res


def get_device_prices(session):
    # Get all devices articles from BD where there is no parsing results today yet
    # SELECT * FROM device WHERE device.product_id NOT IN
    #       (SELECT price.product FROM price WHERE CURRENT_DATE BETWEEN price.start_date AND price.end_date)
    existent_prices = session.query(Price.product).filter(current_date().between(Price.start_date, Price.end_date))
    q = (session
         .query(Device.product_id)
         # .join(Device.device_categories)
         # .join(Category.tasks)
         # .filter(Task.name == "Test")
         .filter(Device.product_id.notin_(existent_prices.subquery()))
         # .limit(1000)
         )
    devices = [dev.product_id for dev in q]

    if len(devices) == 0:
        print("All prices are up to date.")
    else:
        print(f"{len(devices)} price entities should be quiered")

        # SELECT * FROM price WHERE end_date = (select MAX(end_date) from price WHERE end_date < CURRENT_DATE)
        last_date = session.query(sql_max(Price.end_date)).filter(Price.end_date < current_date())

        # Query all price results from last parsing, having devices that are needed.
        # This is used for updating entries if nothing changed from last parsing.
        # In this case we will update end_date, but will not create new row.

        if len(devices) <= 50:  # If we have few results - use cached values
            prev_date_results = (session
                                 .query(Price)
                                 .filter(Price.product.in_(devices))
                                 .filter(Price.end_date.in_(last_date.subquery()))
                                 .all()
                                 )
        else:  # If we have a lot of results - make subquery
            prev_date_results = (session
                                 .query(Price)
                                 .filter(Price.product.in_(q.subquery()))
                                 .filter(Price.end_date.in_(last_date.subquery()))
                                 .all()
                                 )

        # Build hashes from last parsing results
        prev_day_results_hashed = {(entry.product, entry.action_price, entry.base_price, entry.economy): entry
                                   for entry in prev_date_results
                                   }

        # Split info requesting & DB insert/upsert operations into reasonable-sized chunks
        insert_limit = 2000
        slices = list(range(0, len(devices), insert_limit))
        updated_entries = inserted_entries = 0

        for part in slices:
            print(f"Getting part from {part} to {part + insert_limit + 1}.")
            # Make a request to M.Video graphql
            results = asyncio.run(get_prices(devices[part:part + insert_limit + 1]))

            # For each device - check if last parsing results contain similar info
            for i, (key, val) in enumerate(results.items()):
                # Hash = (entry.product, entry.action_price, entry.base_price, entry.economy)
                cur_el_hash = (key, val['actionPrice'], val['basePrice'], val['economy'])

                # Existent entry - will be updated
                if cur_el_hash in prev_day_results_hashed:
                    prev_day_results_hashed[cur_el_hash].end_date = current_date()
                    session.merge(prev_day_results_hashed[cur_el_hash])
                    updated_entries += 1

                # New entry - will be created
                else:
                    cur_price = Price(key, base_price=val['basePrice'], action_price=val['actionPrice'],
                                      economy=val['economy'])
                    session.merge(cur_price)
                    inserted_entries += 1
            session.commit()
        print(f"All prices were processed. {inserted_entries} new entries were inserted, {updated_entries} were updated.")


if __name__ == "__main__":
    session = Session(bind=engine)
    Base.metadata.create_all(bind=engine)

    get_device_prices(session)
