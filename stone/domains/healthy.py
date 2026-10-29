import os
from typing import Annotated

from litestar import Controller, get
from litestar.di import NamedDependency
from msgspec import Meta, Struct, field
from pymongo.asynchronous.database import AsyncDatabase


def rand_str(length: int = 4) -> str:
    """
    生成随机字符串。
    """
    return os.urandom(length).hex()


class HealthyResponse(Struct):
    random: Annotated[str, Meta(title="随机标识")] = field(default_factory=rand_str)
    status: Annotated[str, Meta(description="服务器状态")] = "healthy"


class HealthyController(Controller):
    path = "/healthy"

    @get(summary="健康检查")
    async def find(self, db: NamedDependency[AsyncDatabase]) -> HealthyResponse:
        """
        获取服务健康状态。
        """
        return HealthyResponse()
