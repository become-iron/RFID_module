# -*- coding: utf-8 -*-
import json
from rfid import Reader


def run_reader():
    pass


def process_request(request: str):
    request = json.loads(request)
    tasks = {'inventory': inventory, 'read_tags': read_tags, 'write_tags': write_tags}
    return tasks[request['task']](request['data'])


def inventory(data):
    """
    data
        - id: int
    :param data:
    :return:
    """
    pass


def read_tags(data):
    """
    data
        - id_reader: int
        - serial_nums: list[str]
    :param data:
    :return:
    """
    pass


def write_tags(data):
    """

    data
        - id_reader: int
        - serial_nums:
            - str: str
            - ...
    :param data:
    :return:
    """
    pass
