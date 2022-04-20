"""
Create simulated parsed data message and send it into a Kafka topic.
"""
import argparse
import datetime
import os
import random
import time
from pprint import pprint
from zoneinfo import ZoneInfo

from kafka2api import transform_data, upload_to_api

sample_data = {
    'data': [{'f': {'0': {'v': 1},
                    '1': {'v': 1649936994},
                    '2': {'v': 60.166579},
                    '3': {'v': 24.951239}},
              'time': '2022-04-14T11:49:55.376+00:00'}],
    'device': {'device_id': 'FFFF000000000000',
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


def get_args() -> argparse.Namespace:
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--lat", type=float, default=60.166579, help="Latitude")
    parser.add_argument("--lon", type=float, default=24.951239, help="Longitude")
    parser.add_argument("--button", type=int, default=1, help="Button state (1-255)")
    parser.add_argument("--topic", type=str, help="Kafka parsed data topic name")
    parser.add_argument("--deveui", type=str, default='FFFF000000000000', help="Device EUI")
    parser.add_argument("--api_url", type=str, default='http://127.0.0.1:800/rest/map_data_points/',
                        help="API endpoint URL")
    args = parser.parse_args()
    return args


def main():
    args = get_args()
    data = sample_data
    epoch = int(time.time())
    dl = data["data"][0]
    dl["f"]["0"]["v"] = args.button  # button
    dl["f"]["1"]["v"] = epoch
    dl["f"]["2"]["v"] = round(args.lat + random.random() / 1000, 6)  # lat
    dl["f"]["3"]["v"] = round(args.lon + random.random() / 1000, 6)  # lon

    # Loop forever incoming messages
    data["header"]['end_time'] = datetime.datetime.fromtimestamp(epoch, ZoneInfo("UTC")).isoformat()
    data["header"]['start_time'] = datetime.datetime.fromtimestamp(epoch, ZoneInfo("UTC")).isoformat()
    data["device"]["device_id"] = args.deveui
    data["meta"]['timestamp_received'] = dl["time"] = datetime.datetime.now(ZoneInfo("UTC")).isoformat()
    data["meta"]['timestamp_parsed'] = datetime.datetime.now(ZoneInfo("UTC")).isoformat()
    pprint(data)
    for fbm_data in transform_data(data):
        print("\n\n###################################\nData to POST")
        pprint(fbm_data)
        ok, res = upload_to_api(args.api_url, "xxx", fbm_data)
        print("####################################")
        print(ok, res)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Bye!")
