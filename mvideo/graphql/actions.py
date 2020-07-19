from graphql.device_based_mixin import DeviceBasedMixin
from graphql.graphql import Graphql


class GraphqlActions(DeviceBasedMixin, Graphql):
    """
    Graphql request for current actions
    """

    def parse(self):
        parse_results = {}
        for resp in self.http_responses:
            if isinstance(resp, list):
                n = []
                for r in resp:
                    for rr in r:
                        try:
                            for val in rr["data"]["labels"]:
                                n.append(val)
                        except:
                            # print(rr)
                            pass
                resp = n
            else:
                resp = resp["data"]["labels"]
            try:
                for val in resp:
                    try:
                        cur = {val["productId"]: {"actions": [y["name"] for y in [x for x in val['promotionLabels']]]}}
                        parse_results.update(cur)
                    except Exception as e:
                        print(e)
                        pass
            except KeyError:
                pass
            except Exception as e:
                print("Undefined error", e)

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
