import asyncio
import copy

from aiohttp import ClientSession

from graphql.category_devices import GraphqlCategoryDevices
from graphql.actions import GraphqlActions
from graphql.price import GraphqlPrice
from graphql.device_details import GraphqlDeviceDetails


async def send_request(session: ClientSession, **kwargs) -> dict:
    category = kwargs.pop("category", None)
    req_num = kwargs.pop("req_num", None)
    await asyncio.sleep(0.001)
    try:
        async with session.post(**kwargs) as resp:
            try:
                print(f"Category _{category}_ - request #{req_num}.")
            except:
                pass
            try:
                resp_json = await resp.json()
            except:
                return {}

            if resp.status != 200:
                return {}
            elif resp_json.get("errors", None) is not None:
                return {}
            else:
                try:
                    print(f"Category _{category}_ - request #{req_num} - received.")
                except:
                    pass
                return resp_json

    except ValueError:
        return {}
    return {}

async def get_category_devices(category: int, session: ClientSession) -> list:
    graphql_category = GraphqlCategoryDevices(category)
    cur_request_kwargs = graphql_category.get_request_kwargs()
    cur_request_kwargs["category"] = graphql_category.category
    cur_request_kwargs["req_num"] = 0

    result = await send_request(session, **cur_request_kwargs)
    if result is not None:
        graphql_category.http_responses.append(result)
        try:
            total_devices = graphql_category.http_responses[0]["data"]["searchListing"]["result"]["groups"][0]["total"]
        except KeyError:
            total_devices = 0
        print(f"Category _{category}_ has {total_devices} devices.")
        followed_requests_results = []
        for i, offset in enumerate(
                range(graphql_category.REQUEST_ITEMS_LIMIT, total_devices, graphql_category.REQUEST_ITEMS_LIMIT)):
            cur_request_kwargs = graphql_category.get_request_kwargs(offset, graphql_category.REQUEST_ITEMS_LIMIT)
            cur_request_kwargs["category"] = graphql_category.category
            cur_request_kwargs["req_num"] = i + 1
            followed_requests_results.append(
                send_request(session, **cur_request_kwargs))

        [graphql_category.http_responses.append(await task) for task in followed_requests_results]
        return graphql_category.parse()
    else:
        return []


async def get_device_info_w_slice(session: ClientSession, graphql_instance: object, **kwargs: object) -> list:
    """
    Recursive function to get all results from a given graphql-object
    :param session: aiohttp.ClientSession to manage requests
    :param graphql_instance: Graphql-descendant instance to request from
    :param kwargs: http arguments, which should be passed to http request
    :return:
    """
    request_results = []
    sub_request_kwargs = kwargs
    req_num = sub_request_kwargs.pop("req_num", 0)

    sub_request_kwargs["category"] = graphql_instance.__class__.__name__
    sub_request_kwargs["req_num"] = f"{req_num}"

    http_response = await asyncio.create_task(send_request(session, **sub_request_kwargs))

    if http_response is None:
        cur_devices = sub_request_kwargs["json"]["variables"]["productIds"]
        if len(cur_devices) > 1:
            parts = ([
                cur_devices[:len(cur_devices) // 2],
                cur_devices[len(cur_devices) // 2:]
            ])
            for i, part in enumerate(parts):
                sub_request_kwargs_copy = copy.deepcopy(sub_request_kwargs)
                sub_request_kwargs_copy["json"]["variables"]["productIds"] = part
                sub_request_kwargs_copy["req_num"] = f"{req_num}.{i}"
                request_results.append(await asyncio.create_task(send_request(session, **sub_request_kwargs_copy)))
    else:
        request_results.append(http_response)
    return request_results


async def get_devices_info(
        devices: list,
        session: ClientSession,
        graphql_classes: list = (GraphqlDeviceDetails, GraphqlPrice, GraphqlActions),
        **kwargs
) -> dict:
    """

    :param devices: list of devices' articles to get from site
    :param session: aiohttp.ClientSession to manage requests
    :param graphql_classes: Tuple of graphql-classes (with device mixin) where we will send requests.
    By default - get descriptions, prices & list of actions
    :param kwargs: Additional arguments which will be taken to graphql-classes
    :return: Dictionary with all devices from request, filled with data from requests to graphql-objects
    """
    # Dict container for results from all graphql-objects
    graphql_objects_results = []
    for graphql_class in graphql_classes:  # Iterate through every graphql-object
        graphql_instance = graphql_class(devices, **kwargs)  # Initiate an instance of given graphql-class
        followed_requests_results = []

        # Produce sub-requests with respect to device-per-page limits
        for i, sub_request_kwargs in enumerate(graphql_instance.get_request_kwargs()):
            # Deep copy of request http params to ensure uniqueness of the request
            sub_request_kwargs_copy = copy.deepcopy(sub_request_kwargs)
            # Sub-request identifier (for logging)
            sub_request_kwargs_copy["req_num"] = i
            # Push awaitable with given params
            sub_request_results = asyncio.create_task(
                get_device_info_w_slice(
                    session,
                    graphql_instance,
                    **sub_request_kwargs_copy
                )
            )
            # Adding current sub-request to pending queue
            followed_requests_results.append(sub_request_results)

        await asyncio.gather(*followed_requests_results)

        # Collect all sub-request results for a given graphql-object
        # [graphql_instance.http_responses.append(result) for result in followed_requests_results if result is not None]
        graphql_instance.http_responses.extend([tsk.result()[0] for tsk in followed_requests_results if tsk.result() is not None])

        # Parse all requests of a given graphql object and push results to all-graphql-objects dict
        graphql_objects_results.append(graphql_instance.parse())

    # Gathering of information from all graphql-objects
    # {Device: {param: value}}
    final_dict = {}
    for key in devices:
        final_dict[key] = {}
        for dic in graphql_objects_results:
            if dic.get(str(key), False):
                final_dict[key].update(dic[str(key)])

    # return collected information
    return final_dict


async def get_categories_and_devices(categories: dict, **kwargs) -> dict:
    # aiohttp ClientSession
    async with ClientSession() as session:

        # Making a dictionary with lists of devices in categories
        category_dict = {}
        # {"XXX":[9999,9998 etc], ...,}
        for category_name, category_num in categories.items():
            category_dict[category_name] = await get_category_devices(category_num, session)

        all_devices = []
        # All unique devices
        set([all_devices.extend(devices) for devices in category_dict.values() if devices is not None])
        # Request to graphql objects
        devices_info = await get_devices_info(list(all_devices), session)

    # Provide category number of every device
    for category_num, category_devices in category_dict.items():
        for category_device in category_devices:
            if devices_info.get(category_device, None):
                devices_info[category_device]["category"] = category_num

    # Returning dictionary with all parsed information
    return devices_info


if __name__ == "__main__":
    import time
    from datetime import date
    from os import startfile

    from createExcelWorkbook import process_results_to_xlsx

    s = time.perf_counter()

    bsh_MDA_categories = ({
        "Холодильники и морозильные камеры": 159,
        "Плиты газовые": 110,
        "Посудомоечные машины": 160,
        "Духовые шкафы": 4109,
        "Панели газовые и электрические": 4108,
        "Вытяжки": 2338,
        "Встраиваемые посудомоечные машины": 2333,
        "Холодильники и морозильники встраиваемые": 100,
        "Встраиваемые микроволновые печи": 117,
        "Стиральные машины встраиваемые": 201,
        "Стиральные машины": 89,
    })
    bsh_SDA_categories = ({
        "Пылесосы": 2438,
        "Грили": 198,
        "Кофеварки": 157,
        "Кофеварки капсульного типа": 330,
        "Кофемашины": 155,
        "Кофемолки": 145,
        "Кухонные машины и комбайны": 156,
        "Миксеры и блендеры": 98,
        "Мини-печи": 149,
        "Мультиварки": 180,
        "Мультипекари": 111,
        "Мясорубки": 104,
        "Соковыжималки": 103,
        "Тостеры и ростеры": 99,
        "Утюги": 92,
        "Хлебопечки": 150,
        "Электрочайники": 96

    })
    bro_categories = ({
        "МФУ": 146,
        "Принтеры": 81,
        "Картриджи": 215,
    })

    run_tasks = ({
        "MDA": bsh_MDA_categories,
        "SDA": bsh_SDA_categories,
        "Printers": bro_categories
    })

    parsing_date = date.today()
    date_str = parsing_date.strftime("%d.%m.%Y")

    for task_name, task_categories in run_tasks.items():
        res = asyncio.run(get_categories_and_devices(task_categories))
        save_filename = f"M.Video {task_name} on {date_str}.xlsx"
        print(f"Total entries: {len(res)}")

        filepath = process_results_to_xlsx(res, save_file_name=save_filename, save_file_path="./output/")
        startfile(filepath)

    elapsed = time.perf_counter() - s
    print(f"{__file__} executed in {elapsed:0.2f} seconds.")
