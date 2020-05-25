#  Copyright (c) 2020, Gorelov K.G
#

import copy


class DeviceBasedMixin:
    REQUEST_ITEMS_LIMIT = 360

    def __init__(self, devices, **kwargs):
        super().__init__(**kwargs)
        self.devices = devices

    def get_request_kwargs(self) -> dict:
        mutated_request = copy.deepcopy(self.request)
        for i in range(0, len(self.devices), self.REQUEST_ITEMS_LIMIT):
            mutated_devices = self.devices[i:i + self.REQUEST_ITEMS_LIMIT]
            mutated_request["variables"].update({"productIds": mutated_devices})
            yield ({
                "url": self.URL,
                "json": mutated_request,
                "headers": self.headers
            })

    @property
    def devices(self):
        return self.devices_

    @devices.setter
    def devices(self, devices):
        self.devices_ = [str(el) for el in devices]
        self.request["variables"].update({"productIds": self.devices_})
