class Graphql:
    """
    Base graphql snippet.
    Contains base skeleton for communication with M.Video graphql server
    """
    URL = "https://www.mvideo.ru/.rest/graphql"
    # headers = ({
    #     "origin": "https://www.mvideo.ru",
    #     "content-type": "application/json",
    #     "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"
    # })
    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "cache-control": "no-cache",
        "content-type": "application/json",
        # "cookie": "MVID_CITY_ID=CityCZ_975; MVID_GUEST_ID=14226077692; wurfl_device_id=generic_web_browser; MVID_DELETE_WITH_POPUP=1; _ga=GA1.2.1609371229.1585930684; uxs_uid=b2340730-75c6-11ea-92b2-b9f456c9c818; flocktory-uuid=501fa11a-051b-4174-952e-759bc1ecd59f-3; MVID_GEOLOCATION_NEEDED=false; tmr_lvid=c1489ba51cba686fe623bc87d4f77ceb; tmr_lvidTS=1529587042624; _ym_d=1585930690; _ym_uid=1585930690600774458; _fbp=fb.1.1585930690757.577906676; __zzatgib-w-mvideo=MDA0dBA=Fz2+aQ==; KFP_DID=acb49e91-eac5-1f62-eefd-1d3867f0ff31; MVID_REGION_ID=1; deviceType=desktop; __SourceTracker=yandex__cpc; admitad_deduplication_cookie=yandex__cpc; MVID_DELIVERY_INFO=2; MVID_VIEWED_PRODUCTS=; MVID_VIDEO_REVIEW_NEW=2; MVID_VIDEO_REVIEW=2; MVID_EYEZON_STREAM=1; COMPARISON_INDICATOR=false; abtest_IR=3; uxs_mig=1; _gcl_au=1.1.292301137.1594385072; tmr_reqNum=805; cfidsgib-w-mvideo=r7zAzqfnmnq5sKeV5u+o2jz05x10d83XEVN9TrvUC8hdwm8jjqKOtBc378nryOi262JhnNPwafPbdCt7Xpi31JSVi429hyWiXN0laW3dU5c7W5KYMP1OuO1UlKPgHEk08m8OMFpBc4l79crjTvTDLfhpDpUrUAUclY+mzSE8; JSESSIONID=jnGDfLVdvcYnYLJprfxbf3fJ3yn76QChbWrBkCrxJvvxQl5c1XCy!-282333261; flacktory=no; BIGipServeratg-ps-prod_tcp80=1208278026.20480.0000; BIGipServeratg-ps-prod_tcp80_clone=1208278026.20480.0000; BIGipServeratg-ps-prod_tcp80=1208278026.20480.0000; BIGipServeratg-ps-prod_tcp80_clone=1208278026.20480.0000; CACHE_INDICATOR=false; ADRUM_BTa=R:77|g:82e9755e-b4b8-4c39-a5ab-9cd99c156459|n:customer1_b8e1f0e6-cc5b-4da4-a095-00a44385df2e; ADRUM_BT1=R:77|i:2484|e:45; ADRUM_BTa=R:147|g:556b38db-c75d-4264-ad86-a38c5b4a4fea|n:customer1_b8e1f0e6-cc5b-4da4-a095-00a44385df2e; JSESSION_ID_IR=E10D8DF6B4BFDE990C904D82C6FBEE0D; ADRUM_BT1=R:147|i:5578|e:895; BIGipServericerock-prod=3187989514.20480.0000; bIPs=-957002303",
        "dnt": "1",
        "origin": "https://www.mvideo.ru",
        "pragma": "no-cache",
        # "referer": "https://www.mvideo.ru/stiralnye-i-sushilnye-mashiny-2427/stiralnye-mashiny-89/f/category=uzkie-stiralnye-mashiny-2446?sort=price_asc&reff=menu_main",
        "referer": "https://www.mvideo.ru",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"
    }

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
