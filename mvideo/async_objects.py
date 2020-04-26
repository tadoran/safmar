import copy


class Graphql:
    """
    Base graphql snippet
    """
    URL = "https://www.mvideo.ru/.rest/graphql"
    headers = ({
        "origin": "https://www.mvideo.ru",
        "content-type": "application/json"
    })

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.parsed_results = []
        self.http_requests = []
        self.http_responses = []
        self.request = {}

    def get_request_kwargs(self):
        return ({
            "url": self.URL,
            "json": self.request,
            "headers": self.headers
        })

    def parse(self):
        raise NotImplementedError


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


class GraphqlDeviceDetails(DeviceBasedMixin, Graphql):
    """
    Graphql request for details about devices
    """
    # 100 is maximal limit allowed by Mvideo.Graphql for the query
    REQUEST_ITEMS_LIMIT = 100

    def parse(self):
        parse_results = {}
        for resp in self.http_responses:
            parse_results.update(
                {el["productId"]: {"brand": el['brandName'], "desr": el["name"]["cyrillic"],
                                   "link": el["name"]["latin"]} for el in resp["data"]["products"]}
            )
        return parse_results

    query = """
        query products($productIds: [String]!) {
          products(productIds: $productIds) {
            productId
            name {
              cyrillic
              latin
            }
            brandName
          }
        }
    """
    request = ({
        "operationName": "products",
        "variables": {
        },
        "query": query
    })


class GraphqlPrice(DeviceBasedMixin, Graphql):
    """
    Graphql request for getting prices
    """

    def parse(self):
        parse_results = {}
        for resp in self.http_responses:
            cur = {val["productId"]: {key: el for key, el in val.items() if key != "productId"}
                   for val in resp["data"]["prices"]}
            parse_results.update(cur)
        return parse_results

    query = """
    query prices($productIds: [String]!, $regionId: String!) {
      prices(productIds: $productIds, regionId: $regionId) {
        productId
        actionPrice
        basePrice
        economy
      }
    }
    """

    request = ({
        "operationName": "prices",
        "variables": {
            "regionId": "1"
        },
        "query": query})


class GraphqlActions(DeviceBasedMixin, Graphql):
    """
    Graphql request for current actions
    """

    def parse(self):
        parse_results = {}
        for resp in self.http_responses:
            for val in resp["data"]["labels"]:
                cur = {val["productId"]: {"actions": [y["name"] for y in [x for x in val['promotionLabels']]]}}
                # cur = {val["productId"]: {"actions": {y["name"]:y["tooltip"]["description"] for y in [x for x in val['promotionLabels']]}}}
                parse_results.update(cur)
        return parse_results

    query = """query labels($productIds: [String]!, $parameters: BaseQueryParameters) {
        labels(productIds: $productIds, parameters: $parameters) {
            productId
            promotionLabels {
                name
                tooltip {
                    description
                }
            }
        }
    }"""

    request = ({
        "operationName": "labels",
        "variables": {
        },
        "query": query
    })


class GraphqlCategoryDevices(Graphql):
    REQUEST_ITEMS_LIMIT = 200

    def __init__(self, category, **kwargs):
        super().__init__(**kwargs)
        self.category = category

    def get_request_kwargs(self, offset: int = 0, limit: int = REQUEST_ITEMS_LIMIT) -> dict:
        mutated_request = copy.deepcopy(self.request)
        mutated_request["variables"]["offset"] = offset
        mutated_request["variables"]["limit"] = limit
        return ({
            "url": self.URL,
            "json": mutated_request,
            "headers": self.headers
        })

    def __str__(self):
        return f"<Category {self.category}>"

    @property
    def category(self):
        return self.category_

    @category.setter
    def category(self, category):
        self.category_ = category
        self.request["variables"]["condition"]["categoryId"] = self.category

    def parse(self):
        final_list = []
        [final_list.extend(r["data"]["searchListing"]["result"]["groups"][0]["items"]) for r in self.http_responses]
        self.parsed_results = final_list
        return self.parsed_results

    query = """
        query searchListing($condition: SearchListingCondition!, $order: SearchOrder, $limit: Int!, $offset: Int) {
          searchListing(condition: $condition, order: $order, limit: $limit, offset: $offset) {
            result {
              groups {
                total
                items
              }
            }
          }
        }
        """
    request = ({
        "operationName": "searchListing",
        "variables":
            {"condition":
                {
                    "shopId": None,
                    "availableNow": "false",
                },
                "limit": REQUEST_ITEMS_LIMIT,
                "offset": 0,
                "order": "DEFAULT"
            },
        "query": query
    })


class GraphqlCategoryDevicesBshOnly(GraphqlCategoryDevices):
    def __init__(self, category, **kwargs):
        super().__init__(category, **kwargs)
        self.request["variables"]["condition"]["filters"] = [{"name": "vendor", "values": ["bosch", "siemens"]}]
