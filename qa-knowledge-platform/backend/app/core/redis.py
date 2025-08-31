import redis.asyncio as redis
from app.core.config import settings

# 创建Redis连接池
redis_pool = redis.ConnectionPool.from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True
)

# 创建Redis客户端
redis_client = redis.Redis(connection_pool=redis_pool)


async def get_redis():
    """获取Redis客户端"""
    return redis_client


async def close_redis():
    """关闭Redis连接"""
    await redis_client.close()