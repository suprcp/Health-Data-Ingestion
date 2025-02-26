import redis
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging
import time
import random

from .database import engine
from .models import HealthMetric
from .config import REDIS_HOST, REDIS_PORT, REDIS_DB

logger = logging.getLogger(__name__)


class HealthDataStream:
    def __init__(self):
        self.redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
        self.stream = 'health-data-stream'
        self.group = 'health-data-group'
        self.consumer = f"consumer-{int(time.time())}"
        self.running = True

        try:
            self.redis_client.xgroup_create(self.stream, self.group, id='$', mkstream=True)
            logger.info(f"Created consumer group: {self.group}")
        except redis.exceptions.ResponseError as e:
            if "BUSYGROUP" in str(e):
                logger.info(f"Consumer group already exists: {self.group}")
            else:
                logger.error(f"Error creating group: {e}")
                raise

    def add_metric(self, user_id, heart_rate, steps, calories):
        metric = {
            'user_id': str(user_id),
            'heart_rate': str(heart_rate),
            'steps': str(steps),
            'calories': str(calories),
            'timestamp': datetime.utcnow().isoformat()
        }

        message_id = self.redis_client.xadd(self.stream, metric)
        logger.info(f"Added metric for user {user_id}. Msg ID: {message_id}")
        return message_id

    def process_stream(self, batch_size=10, block_ms=5000):
        SessionLocal = sessionmaker(bind=engine)
        self.running = True

        logger.info(f"HealthDataStream is running. Listening as {self.consumer}.")

        retry_attempt = 0

        while self.running:
            try:
                messages = self.redis_client.xreadgroup(
                    self.group,
                    self.consumer,
                    {self.stream: '>'},
                    count=batch_size,
                    block=block_ms
                )

                if not messages:
                    time.sleep(0.1)
                    continue

                for stream, message_list in messages:
                    for message_id, message_data in message_list:
                        metric = {k.decode(): v.decode() for k, v in message_data.items()}
                        logger.info(f"Processing message {message_id}: {metric}")

                        db = SessionLocal()
                        try:
                            new_metric = HealthMetric(
                                user_id=int(metric['user_id']),
                                timestamp=datetime.fromisoformat(metric['timestamp']),
                                heart_rate=int(metric['heart_rate']),
                                steps=int(metric['steps']),
                                calories=float(metric['calories'])
                            )

                            db.add(new_metric)
                            db.commit()

                            self.redis_client.xack(self.stream, self.group, message_id)
                            logger.info(f"Successfully processed metric for user {metric['user_id']}")
                        except Exception as e:
                            db.rollback()
                            logger.error(f"Couldn't save metric: {e}")
                        finally:
                            db.close()
            except redis.exceptions.ConnectionError as e:
                retry_attempt += 1
                delay = min(10, int(random.uniform(2, 2 ** retry_attempt)))
                logger.error(f"Redis connection error.Retrying in {delay:.1f} sec... Error: {e}")
                time.sleep(delay)
            except Exception as e:
                logger.error(f"Unexpected error happened: {e}")
                time.sleep(1)

        logger.info("Stream processor stopped")

    def shutdown_processor(self):
        logger.info("Shutdown request received.")
        self.running = False


stream_processor = HealthDataStream()