"""
Consume new serialised feedback messages from Kafka topic and send the data to other endpoint using httpx.
"""

import json
import logging
import os
import time
from typing import Tuple, Optional

import httpx
import requests

from fvhiot.utils import init_script
from fvhiot.utils.kafka import get_kafka_consumer_by_envs


def upload_to_api(api_url: str, data: dict) -> Tuple[bool, Optional[requests.Response]]:
    """Upload given data to rest API and return httpx.response or None (in the case of exception)."""
    headers = {
        "User-Agent": "fbm-feedback_forward/0.0.1 (https://github.com/ForumViriumHelsinki/FVHFeedbackMap)",
        "Content-Type": "application/json",
    }
    ok = False
    try:
        logging.info(f"Making POST request to {api_url} with data: {data}")
        res = httpx.post(api_url, headers=headers, json=data, timeout=15)
        if 200 <= res.status_code < 300:
            logging.info(f"Request to {api_url} successful: {res.status_code}")
            ok = True
        else:
            logging.warning(f"Request to {api_url} failed: {res.status_code}")
            logging.debug(res.content)
    except Exception:
        logging.exception(f"Failed to POST to {api_url}")
        raise
    return ok, res


def main():
    init_script()
    parsed_data_topic = os.getenv("KAFKA_FORWARD_TOPIC_NAME")
    logging.info(f"Start listening Kafka topic: {parsed_data_topic}")
    # Create Kafka consumer for incoming messages
    consumer = get_kafka_consumer_by_envs(parsed_data_topic)
    api_url = os.getenv("FORWARD_API_URL")
    logging.info(f"Sending data to: {api_url}")
    if consumer is None:
        logging.critical("Kafka connection failed, exiting.")
        time.sleep(10)
        exit(1)
    # Loop forever for incoming messages
    for msg in consumer:
        data = json.loads(msg.value.decode("utf-8"))
        ok, res = upload_to_api(api_url, data)
        logging.info(f"Result for upload: {ok}, {res.content}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Bye!")
