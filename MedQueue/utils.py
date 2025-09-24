import redis
from django.conf import settings

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True,  # Set it to False if you want to work with binary data.
)

redis_expire_pubsub = redis_client.pubsub()
redis_expire_pubsub.subscribe('__keyevent@0__:expired')