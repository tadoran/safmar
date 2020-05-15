import copy

from graphql.graphql import Graphql


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
        [
            final_list.extend(
                r["data"]["searchListing"]["result"]["groups"][0]["items"]
            )
            for r in self.http_responses
            if not r is None
        ]
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