import motor.motor_asyncio
from app import settings

# from redis.asyncio import Redis

# redis_db: Redis = Redis.from_url(settings.REDIS_URI, decode_responses=True)

DATABASE_URL = settings.MONGODB_URI
client = motor.motor_asyncio.AsyncIOMotorClient(
    DATABASE_URL, uuidRepresentation="standard"
)
db = client[settings.MONGODB_NAME]