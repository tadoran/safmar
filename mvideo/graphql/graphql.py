class Graphql:
    """
    Base graphql snippet.
    Contains base skeleton for communication with M.Video graphql server
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
        # self.request = {}

    def get_request_kwargs(self):
        return ({
            "url": self.URL,
            "json": self.request,
            "headers": self.headers
        })

    def parse(self):
        raise NotImplementedError
