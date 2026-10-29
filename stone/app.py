import logging
from contextlib import asynccontextmanager

import pymongo
from litestar import Litestar
from litestar.config.cors import CORSConfig
from litestar.datastructures import State
from litestar.di import Provide
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.database import Database

from stone.domains.healthy import HealthyController
from stone.domains.token import TokenController
from stone.settings import Settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def db_context(app: Litestar):
    """
    异步上下文管理器，用于连接和关闭 MongoDB 数据库连接。
    """
    uri = settings.mongo_uri
    name = settings.mongo_name
    # 连接 MongoDB 数据库
    client = pymongo.AsyncMongoClient(uri)
    db = client[name]
    app.state["db"] = db
    yield
    await client.close()


async def provide_db(state: State) -> AsyncDatabase:
    """
    提供 MongoDB 数据库连接。
    """
    return state["db"]


async def provide_settings(state: State) -> Settings:
    return state["settings"]


def create_app(settings: Settings | None = None) -> Litestar:
    return Litestar(
        debug=settings.debug,
        route_handlers=[HealthyController, TokenController],
        lifespan=[db_context],
        dependencies={
            "db": Provide(provide_db),
            "settings": Provide(provide_settings),
        },
        cors_config=CORSConfig(
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        ),
    )


settings = Settings()
app = create_app(settings)
