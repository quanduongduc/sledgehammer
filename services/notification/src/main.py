import json
import logging
import os
from consumer import consumer
from confluent_kafka import KafkaError
from topic_handler import TopicHandler

# Specify the log folder and file name
log_folder = './logs'
log_file = 'error.log'

# Combine the log folder and file name to create the full log file path
log_file_path = os.path.join(log_folder, log_file)

# Configure logging
logging.basicConfig(
    level=logging.ERROR,  # Set the desired logging level
    format="%(asctime)s [%(levelname)s] - %(message)s",
    filename=log_file_path,  # Log file path in the specified folder
    filemode="a"  # Append mode
)

logger = logging.getLogger(__name__)

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                print('Reached the end of the partition')
            else:
                logger.error('Kafka Error: {}'.format(msg.error()))
        else:
            try:
                message_object = json.loads(msg.value())
                topic = msg.topic()
                topic_handler = TopicHandler(topic)
                topic_handler.handle(message_object)
            except json.JSONDecodeError as e:
                logger.error('Error decoding JSON message: {}'.format(e))
            except Exception as ex:
                logger.error('General Exception: {}'.format(ex))

except KeyboardInterrupt:
    pass
except Exception as ex:
    logger.error('General Exception: {}'.format(ex))
finally:
    consumer.close()