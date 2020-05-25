from graphql.device_based_mixin import DeviceBasedMixin
from graphql.graphql import Graphql


class GraphqlActions(DeviceBasedMixin, Graphql):
    """
    Graphql request for current actions
    """

    def parse(self):
        parse_results = {}
        for resp in self.http_responses:
            try:
                for val in resp["data"]["labels"]:
                    cur = {val["productId"]: {"actions": [y["name"] for y in [x for x in val['promotionLabels']]]}}
                    parse_results.update(cur)
            except KeyError:
                pass
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
