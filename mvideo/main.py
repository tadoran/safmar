from get_devices_info import get_devices_information
from get_new_devices import get_new_devices
from get_prices import get_device_prices
from get_actions import get_device_actions
from sql.base import Session, engine, Base

import time

if __name__ == "__main__":
    t1 = time.perf_counter()

    session = Session(bind=engine)
    Base.metadata.create_all(bind=engine)

    get_new_devices(session)
    get_devices_information(session)
    get_device_prices(session)
    get_device_actions(session)

    t2 = time.perf_counter()
    print(f'Finished in {t2 - t1} seconds')
