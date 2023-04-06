import json
import logging
import os

from django.core import serializers
from django.db.models.signals import post_save
from django.dispatch import receiver
from kafka import KafkaProducer

from feedback_map.models.map_data_points import MapDataPoint

# Create a Kafka producer instance. This will raise an exception if the connection fails.
# Producer will live for the duration of the app.
if os.getenv("KAFKA_BOOTSTRAP_SERVERS"):
    try:
        producer = KafkaProducer(
            bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "").split(","),
            security_protocol=os.getenv("KAFKA_SECURITY_PROTOCOL", "PLAINTEXT"),
            ssl_cafile=os.getenv("KAFKA_SSL_CA_LOCATION"),
            ssl_certfile=os.getenv("KAFKA_ACCESS_CERT"),
            ssl_keyfile=os.getenv("KAFKA_ACCESS_KEY"),
            sasl_mechanism=os.getenv("KAFKA_SASL_MECHANISMS"),
            sasl_plain_username=os.getenv("KAFKA_SASL_USERNAME"),
            sasl_plain_password=os.getenv("KAFKA_SASL_PASSWORD"),
        )
        logging.info(
            "Kafka producer successfully connected to {}.".format(
                os.getenv("KAFKA_BOOTSTRAP_SERVERS")
            )
        )
    except Exception as e:
        logging.critical(f"Kafka producer failed to connect. {e}")
        raise
else:
    producer = None


@receiver(post_save, sender=MapDataPoint)
def send_to_kafka(sender, instance, created, **kwargs):
    if producer is not None and os.getenv("KAFKA_FORWARD_TOPIC_NAME") and created:
        # serialize instance to json using Django's serializer, this will take care of datetime and other types
        data = json.loads(serializers.serialize("json", [instance]))[0]
        # create a dict with the fields we want to send to Kafka
        keys = ["created_at", "lat", "lon", "image", "comment", "tags", "device_id"]
        payload = {"id": instance.id}
        for key in keys:
            payload[key] = data["fields"][key]
        # convert dict to bytes
        pl_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
        logging.info(
            f"Sending {pl_bytes} to Kafka topic {os.getenv('KAFKA_FORWARD_TOPIC_NAME')}"
        )
        producer.send(os.getenv("KAFKA_FORWARD_TOPIC_NAME"), pl_bytes)
        # flush the producer to ensure the message is sent
        producer.flush()
    else:
        pass  # new instance was not created, so we don't need to send it to Kafka
