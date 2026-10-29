import time
from typing import Annotated, Union

import jwt
from argon2 import PasswordHasher
from bson import ObjectId
from litestar import Controller, post
from litestar.di import NamedDependency
from litestar.params import JSONBody
from msgspec import Meta, Struct, field
from pymongo.asynchronous.database import AsyncDatabase


class TokenCreateByPasswordRequest(Struct, tag_field="grant_type", tag="password"):
    username: Annotated[str, Meta(title="用户名")]
    password: Annotated[str, Meta(title="密码")]


class TokenCreateByRefreshTokenRequest(Struct, tag_field="grant_type", tag="refresh"):
    refresh_token: Annotated[str, Meta(title="刷新令牌")]


class TokenCreateResponse(Struct):
    access_token: Annotated[str, Meta(title="访问令牌")]
    refresh_token: Annotated[str, Meta(title="刷新令牌")]
    token_type: Annotated[str, Meta(title="令牌类型")] = "Bearer"


class TokenController(Controller):
    path = "/tokens"

    @post(summary="创建令牌")
    async def create(
        self,
        data: JSONBody[TokenCreateByPasswordRequest | TokenCreateByRefreshTokenRequest],
        db: NamedDependency[AsyncDatabase],
    ) -> TokenCreateResponse:
        """
        创建令牌。
        """
        if isinstance(data, TokenCreateByPasswordRequest):
            # 校验用户名密码
            entry = await db.users.find_one({"username": data.username})
            if entry is None:
                raise HTTPException(status_code=400, detail="用户名密码错误")
            ph = PasswordHasher()
            if not ph.verify(entry["password"], data.password):
                raise HTTPException(status_code=400, detail="用户名密码错误")
        else:
            # 校验刷新令牌
            try:
                claims = jwt.decode(
                    data.refresh_token,
                    settings.jwt_refresh_key,
                    algorithms=[settings.jwt_algorithm],
                )
            except:
                raise HTTPException(status_code=400, detail="刷新令牌错误")
            entry = await db.users.find_one({"_id": ObjectId(claims["sub"])})
            if entry is None:
                raise HTTPException(status_code=400, detail="刷新令牌错误")
        user_id = str(entry["_id"])
        access_token = jwt.encode(
            {"sub": user_id, "exp": time.time() + settings.jwt_access_expire},
            settings.jwt_access_key,
            algorithm=settings.jwt_algorithm,
        )
        refresh_token = jwt.encode(
            {"sub": user_id, "exp": time.time() + settings.jwt_refresh_expire},
            settings.jwt_refresh_key,
            algorithm=settings.jwt_algorithm,
        )
        return TokenCreateResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )
