import asyncio

from aiohttp import ClientSession
from sqlalchemy.sql.functions import current_date, max as sql_max

from graphql.actions import GraphqlActions
from graphql_get_async import get_devices_info
from sql.base import Session, engine, Base
from sql.device import Device
from sql.category import Category
from sql.task import Task
from sql.action import Action
from sql.device_action import DeviceAction


async def get_actions(devices: list) -> dict:
    """Get Graphql prices data
    :param devices - list of devices articles
    :returns dict(article:{'actionPrice':str, 'basePrice':int, 'economy': int}, ...)"""
    async with ClientSession() as session:
        res = await get_devices_info(devices, session, [GraphqlActions])
        return res


def get_device_actions(session):
    # Get all devices articles from BD where there is no parsing results today yet
    # SELECT * FROM device WHERE device.product_id NOT IN
    #   (SELECT device_action.product FROM device_action
    #       WHERE CURRENT_DATE BETWEEN device_action.start_date AND device_action.end_date)
    existent_prices = (session
                              .query(DeviceAction.product_id)
                              .filter(
                                      current_date().between(DeviceAction.start_date, DeviceAction.end_date)
                                     )
                      )

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
        print("All actions are up to date.")
    else:
        print(f"{len(devices)} price entities should be quiered")

        # SELECT * FROM device_action
        # WHERE end_date = (select MAX(end_date) from device_action WHERE end_date < CURRENT_DATE)
        last_date = session.query(sql_max(DeviceAction.end_date)).filter(DeviceAction.end_date < current_date())

        # Query all DeviceAction results from last parsing, having devices that are needed.
        # This is used for updating entries if nothing changed from last parsing.
        # In this case we will update end_date, but will not create new row.

        if len(devices) <= 50:  # If we have few results - use cached values
            prev_date_results = (session
                                 .query(DeviceAction)
                                 .filter(DeviceAction.product_id.in_(devices))
                                 .filter(DeviceAction.end_date.in_(last_date.subquery()))
                                 .all()
                                 )
        else:  # If we have a lot of results - make subquery
            prev_date_results = (session
                                 .query(DeviceAction)
                                 .filter(DeviceAction.product_id.in_(q.subquery()))
                                 .filter(DeviceAction.end_date.in_(last_date.subquery()))
                                 .all()
                                 )

        # Build hashes from last parsing results
        prev_day_results_hashed = {(entry.product_id, entry.action): entry
                                   for entry in prev_date_results
                                   }

        # Build hashes to all known actions
        all_actions = session.query(Action).all()
        all_actions_hashed = {action.name: action for action in all_actions}

        # Split info requesting & DB insert/upsert operations into reasonable-sized chunks
        insert_limit = 1000
        slices = list(range(0, len(devices), insert_limit))

        updated_entries = inserted_entries = empty_entries = 0

        for part in slices:
            print(f"Getting part from {part} to {part + insert_limit + 1}.")
            # Make a request to M.Video graphql
            results = asyncio.run(get_actions(devices[part:part + insert_limit + 1]))

            # For each device - check if last parsing results contain similar info
            for i, (key, val) in enumerate(results.items()):

                # Special mark if there are no actions for the device (that is for not querying these devices again)
                if len(val.get("actions", [])) == 0:
                    val["actions"] = ["None"]

                for action in val.get("actions", None):
                    # If currently viewed action is new - put it to DB & update actions hash-table
                    if not all_actions_hashed.get(action, None):
                        action_obj = session.merge(Action(action))
                        session.commit()
                        print(f"New action was found - '{action}'")
                        all_actions_hashed[action_obj.name] = action_obj
                    else:
                        action_obj = all_actions_hashed[action]

                    # Hash for device_action (entry.product, Action.id)
                    cur_el_hash = (key, action_obj.id)

                    # Existent entry - will be updated
                    if cur_el_hash in prev_day_results_hashed:
                        prev_day_results_hashed[cur_el_hash].end_date = current_date()
                        session.merge(prev_day_results_hashed[cur_el_hash])
                        updated_entries += 1

                    # New entry - will be created
                    else:
                        device_action = DeviceAction(product=key, action=action_obj.id)
                        session.add(device_action)
                        inserted_entries += 1

                    if action_obj.name == "None":
                        empty_entries += 1

            session.commit()
        print(f"All actions were processed. {inserted_entries} new entries were inserted, {updated_entries} were updated.")
        if empty_entries > 0:
            print(f"{empty_entries} entries are submitted empty (no actions)")


if __name__ == "__main__":
    session = Session(bind=engine)
    Base.metadata.create_all(bind=engine)

    get_device_actions(session)
