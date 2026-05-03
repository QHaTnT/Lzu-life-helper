"""
统一响应封装：{ code, msg, data }
- 业务代码使用 ok() / fail() 即可返回标准结构
- 所有 HTTPException 通过 add_exception_handlers 自动转为统一结构
- 未处理异常返回 500 + msg
code 约定：
    0        成功
    4xx/5xx  直接复用 HTTP 状态码
    1xxx     业务错误（由调用方显式指定）
"""
from typing import Any, Optional
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


def ok(data: Any = None, msg: str = "success") -> dict:
    """成功响应"""
    return {"code": 0, "msg": msg, "data": data}


def fail(msg: str = "error", code: int = 400, data: Any = None) -> JSONResponse:
    """失败响应（直接作为路由返回值）"""
    return JSONResponse(
        status_code=code if 400 <= code < 600 else 400,
        content={"code": code, "msg": msg, "data": data},
    )


def add_exception_handlers(app) -> None:
    """注册全局异常处理器，把 HTTPException / 验证错误 / 未知异常统一包装"""

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": exc.status_code, "msg": str(exc.detail), "data": None},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        msg = "参数校验失败"
        errors = exc.errors()
        if errors:
            first = errors[0]
            loc = ".".join(str(x) for x in first.get("loc", []) if x != "body")
            msg = f"{loc}: {first.get('msg', msg)}" if loc else first.get("msg", msg)
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"code": 422, "msg": msg, "data": exc.errors()},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"code": 500, "msg": f"服务器内部错误：{exc}", "data": None},
        )
