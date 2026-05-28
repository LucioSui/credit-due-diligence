"""Redis 缓存客户端 — 开发环境优雅降级为内存缓存。"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import Any

import redis.asyncio as aioredis

from config import settings

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis 缓存客户端。

    如果 Redis 不可用（开发环境常见），自动降级为内存 dict 缓存。
    """

    def __init__(self) -> None:
        self._redis: aioredis.Redis | None = None
        self._fallback_cache: dict[str, tuple[dict, float]] = {}
        self._using_fallback: bool = False

    # ------------------------------------------------------------------
    # 公共接口
    # ------------------------------------------------------------------

    async def connect(self) -> None:
        """尝试连接 Redis；失败则启用内存缓存降级。"""
        try:
            self._redis = aioredis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=2,
            )
            await self._redis.ping()
            logger.info("Redis 连接成功: %s", settings.REDIS_URL)
        except Exception:
            self._redis = None
            self._using_fallback = True
            logger.warning(
                "Redis 不可用 (%s)，降级为内存缓存", settings.REDIS_URL
            )

    async def get(self, key: str) -> dict | None:
        """获取缓存，返回反序列化的 dict。"""
        if self._using_fallback:
            return self._get_fallback(key)
        if self._redis is None:
            return None
        raw = await self._redis.get(key)
        if raw is None:
            return None
        return json.loads(raw)

    async def set(self, key: str, value: dict, ttl: int = 86400) -> None:
        """设置缓存，TTL 默认 24h。"""
        serialized = json.dumps(value, ensure_ascii=False)
        if self._using_fallback:
            self._set_fallback(key, value, ttl)
            return
        if self._redis is None:
            return
        await self._redis.setex(key, ttl, serialized)

    async def delete(self, key: str) -> None:
        """删除缓存。"""
        if self._using_fallback:
            self._fallback_cache.pop(key, None)
            return
        if self._redis is None:
            return
        await self._redis.delete(key)

    async def close(self) -> None:
        """关闭连接。"""
        if self._redis is not None:
            await self._redis.close()
            self._redis = None
        self._fallback_cache.clear()

    # ------------------------------------------------------------------
    # 内存缓存 fallback
    # ------------------------------------------------------------------

    def _get_fallback(self, key: str) -> dict | None:
        entry = self._fallback_cache.get(key)
        if entry is None:
            return None
        value, expire_at = entry
        if time.monotonic() > expire_at:
            self._fallback_cache.pop(key, None)
            return None
        return value

    def _set_fallback(self, key: str, value: dict, ttl: int) -> None:
        self._fallback_cache[key] = (value, time.monotonic() + ttl)

    # ------------------------------------------------------------------
    # 缓存键辅助方法
    # ------------------------------------------------------------------

    @staticmethod
    def make_qcc_key(entity: str, resource: str) -> str:
        """Generate a cache key for QCC data.

        Example: ``qcc:company:阿里巴巴集团控股有限公司``
        """
        return f"qcc:{resource}:{entity}"


# Module-level singleton
redis_cache = RedisCache()
