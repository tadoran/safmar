from graphql.device_based_mixin import DeviceBasedMixin
from graphql.graphql import Graphql


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