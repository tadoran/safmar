from graphql.device_based_mixin import DeviceBasedMixin
from graphql.graphql import Graphql


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
                {el["productId"]: {
                    "brand": el['brandName'],
                    "desr": el["name"]["cyrillic"],
                    "link": el["name"]["latin"],
                    "imgUrl": el["imageURL"],
                } for el in resp["data"]["products"]
                }
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
            imageURL
          }
        }
    """
    request = ({
        "operationName": "products",
        "variables": {
        },
        "query": query
    })
