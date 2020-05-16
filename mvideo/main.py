from sql.base import Session, engine, Base

from get_new_devices import get_new_devices
from get_devices_info import get_devices_information
from get_prices import get_device_prices

if __name__ == "__main__":
    session = Session(bind=engine)
    Base.metadata.create_all(bind=engine)

    get_new_devices(session)
    get_devices_information(session)
    get_device_prices(session)
