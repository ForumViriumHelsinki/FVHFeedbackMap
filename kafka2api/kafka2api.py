"""
Consume parsed data messages from Kafka topic and send the data to FVHFeedbackMap rest endpoint using requests.
"""

import datetime
import logging
import os
import time
from pprint import pformat, pprint
from typing import Tuple, Optional
from zoneinfo import ZoneInfo

import requests

from fvhiot.utils import init_script
from fvhiot.utils.data import data_unpack
from fvhiot.utils.kafka import get_kafka_consumer_by_envs

sample_data = {
    'data': [{'f': {'0': {'v': 2},
                    '1': {'v': 1649936994},
                    '2': {'v': 60.166579},
                    '3': {'v': 24.951239}},
              'time': '2022-04-14T11:49:55.376+00:00'}],
    'device': {'device_id': 'FFFF000000000001',
               'device_metadata': {'description': 'broker.fvh.io',
                                   'device_in_redis': 'No',
                                   'device_type': 'LoRaWAN 1.0 - class A - ETSI - '
                                                  'Rx2_SF12 - no ADR',
                                   'name': 'IoT Device 1',
                                   'parser_module': 'fvhiot.parsers.fvhgeneric',
                                   'pseudonym': '',
                                   'state': 'Production'},
               'device_state': {'created_at': '2022-04-14T10:18:37.551589+00:00',
                                'last_seen_at': None,
                                'location': 'Placeholder',
                                'state': 'Production',
                                'updated_at': '2022-04-14T10:18:37.692314+00:00'}},
    'header': {'columns': {'0': {'name': 'button0'},
                           '1': {'name': 'epoch'},
                           '2': {'name': 'lat'},
                           '3': {'name': 'lon'}},
               'end_time': '2022-04-14T11:49:55.376+00:00',
               'start_time': '2022-04-14T11:49:55.376+00:00'},
    'meta': {'timestamp_parsed': '2022-04-14T11:49:56.049999+00:00',
             'timestamp_received': '2022-04-14T11:49:55.376000+00:00'},
    'version': '1.0'
}


def upload_to_api(api_url: str, api_token: str, data: dict) -> Tuple[bool, Optional[requests.Response]]:
    """Upload given data to rest API and return requests.Response or None (in the case of exception)."""
    headers = {
        "X-API-TOKEN": api_token,
        "User-Agent": "iot-device-upload/0.0.1 (https://github.com/ForumViriumHelsinki/FVHFeedbackMap)",
    }
    res = None
    ok = False
    try:
        res = requests.post(api_url, headers=headers, json=data)
        if 200 <= res.status_code < 300:
            logging.info(f"Request to {api_url} successful: {res.status_code}")
            ok = True
        else:
            logging.warning(f"Request to {api_url} failed: {res.status_code}")
            logging.info(res.content)
    except Exception:
        logging.exception(f"Failed to POST to {api_url}")
    return ok, res


def transform_data(data: dict) -> dict:
    pprint(data)
    header = data["header"]
    datalines = data["data"]
    device_id = data["device"]["device_id"]
    for dl in datalines:
        flatted = {}  # simplify parsed data payload to one-level dict
        for dk in dl["f"].keys():
            flatted[header["columns"][dk]["name"]] = dl["f"][dk]["v"]
        pprint(flatted)
        tp = datetime.datetime.fromtimestamp(flatted["epoch"], ZoneInfo("UTC")).isoformat()
        data_to_upload = {
            'device_id': device_id,
            'lat': flatted["lat"],
            'lon': flatted["lon"],
            'comment': '',
            'button_position': flatted["button0"],
            'time_received': data["meta"]["timestamp_received"],
            'time_pressed': tp,
        }
        yield data_to_upload


def main():
    init_script()
    parsed_data_topic = os.getenv("KAFKA_PARSED_DATA_TOPIC_NAME")
    # Create Kafka consumer for incoming raw data messages
    # TODO: use aiokafka
    consumer = get_kafka_consumer_by_envs(parsed_data_topic)
    api_url = os.getenv("FVHFEEDBACKMAP_API_URL")
    if consumer is None:
        logging.critical("Kafka connection failed, exiting.")
        time.sleep(10)
        exit(1)
    # Loop forever incoming messages
    for msg in consumer:
        data = data_unpack(msg.value)
        if len(data["data"]) == 0:
            logging.info("Got parsed data having no datalines: {}".format(pformat(data)))
            continue
        data = sample_data
        for data_to_upload in transform_data(data):
            pprint(data_to_upload)
            ok, res = upload_to_api(api_url, "api_token_should_be_here", data_to_upload)
            print(ok, res)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Bye!")
