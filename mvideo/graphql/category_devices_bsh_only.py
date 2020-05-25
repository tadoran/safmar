#  Copyright (c) 2020, Gorelov K.G
#

from graphql.category_devices import GraphqlCategoryDevices


class GraphqlCategoryDevicesBshOnly(GraphqlCategoryDevices):
    def __init__(self, category, **kwargs):
        super().__init__(category, **kwargs)
        self.request["variables"]["condition"]["filters"] = [{"name": "vendor", "values": ["bosch", "siemens"]}]
