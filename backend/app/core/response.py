"""
统一响应封装模块。

这个文件定义了整个 API 的标准响应格式：
  成功响应：{"code": 0, "msg": "success", "data": 具体数据}
  失败响应：{"code": 错误码, "msg": "错误描述", "data": 附加信息}

为什么需要统一响应格式？
  1. 前端处理方便：前端只需要按一种格式解析响应，不需要针对不同接口写不同的解析逻辑。
  2. 调试方便：后端排查问题时，通过 code 字段就能快速判断是成功还是哪种失败。
  3. 文档化：code 字段的含义可以形成一份错误码文档，方便前后端协作。

code 约定：
  0        - 操作成功
  4xx/5xx  - HTTP 状态码级别的错误（如 400 参数错误、401 未认证、404 资源不存在）
  1xxx     - 业务级别的错误（如 1001 用户名已存在、1002 密码错误）

这个文件还注册了全局异常处理器，把所有未处理的异常都转换成统一格式的响应，
确保前端永远不会收到非标准格式的错误信息。
"""

# 导入 Any 类型：表示 data 字段可以是任意类型的数据（dict、list、str、None 等）。
# 导入 Optional 类型：表示参数可以传也可以不传（即默认值为 None）。
from typing import Any, Optional

# 导入 Request 类：用于在异常处理器中获取请求信息（比如请求路径、请求方法）。
from fastapi import Request

# 导入 status 模块：包含所有 HTTP 状态码的常量，
# 比如 status.HTTP_422_UNPROCESSABLE_ENTITY 代表 422，
# 比 status.HTTP_500_INTERNAL_SERVER_ERROR 代表 500。
# 使用常量比直接写数字更可读、更不容易出错。
from fastapi import status

# 导入 RequestValidationError：FastAPI 参数校验失败时抛出的异常类型。
# 当请求的参数（路径参数、查询参数、请求体）不符合定义的类型或约束时，会抛出这个异常。
from fastapi.exceptions import RequestValidationError

# 导入 JSONResponse：FastAPI 提供的 JSON 响应类。
# 它可以设置 HTTP 状态码和返回的 JSON 内容。
# 与普通的 dict 返回不同，JSONResponse 可以精确控制 HTTP 状态码。
from fastapi.responses import JSONResponse

# 导入 StarletteHTTPException：Starlette 框架的 HTTP 异常类。
# FastAPI 是基于 Starlette 构建的，所有 HTTP 异常（如 404 Not Found、403 Forbidden）
# 都是这个类的实例。需要导入它来注册对应的异常处理器。
from starlette.exceptions import HTTPException as StarletteHTTPException


# ==================== 成功响应 ====================

def ok(data: Any = None, msg: str = "success") -> dict:
    """
    构造成功响应。

    参数：
      data：成功时返回给前端的数据。可以是字典、列表、字符串等任意类型。
        默认为 None，表示没有数据需要返回（比如删除操作成功）。
      msg：提示信息，默认为 "success"。可以传中文提示，比如 "注册成功"。

    返回值：
      一个字典，格式为 {"code": 0, "msg": msg, "data": data}。
      注意：这里返回的是 dict 而不是 JSONResponse。
      FastAPI 会自动将 dict 转换为 JSON 响应，并设置 Content-Type 为 application/json。

    为什么 code 用 0 而不是 200？
      HTTP 状态码 200 表示"请求成功"，已经在 HTTP 层面体现了。
      业务层的 code 字段用 0 表示成功是一种常见约定（类似于 C 语言中 0 表示成功）。
      这样可以区分"HTTP 请求成功但业务失败"的情况，比如 HTTP 200 + code=1001（业务错误码）。
    """
    return {"code": 0, "msg": msg, "data": data}


def fail(msg: str = "error", code: int = 400, data: Any = None) -> JSONResponse:
    """
    构造失败响应。

    参数：
      msg：错误描述信息，会返回给前端显示给用户。比如 "用户名已存在"。
      code：业务错误码，默认 400。可以是 HTTP 状态码（400-599），
        也可以是业务错误码（如 1001、1002）。
      data：附加错误数据，可以是详细的错误信息、字段校验结果等。

    返回值：
      JSONResponse 对象，包含 HTTP 状态码和 JSON 内容。

    为什么返回 JSONResponse 而不是 dict？
      因为失败响应需要设置精确的 HTTP 状态码。
      如果返回 dict，FastAPI 默认会设置 HTTP 200，即使业务层报了错误。
      使用 JSONResponse 可以明确指定 HTTP 状态码（如 400、401、404、500）。

    HTTP 状态码设置逻辑（第 26 行）：
      status_code=code if 400 <= code < 600 else 400
      如果 code 在 400-599 范围内（即本身就是 HTTP 状态码），就用 code 作为 HTTP 状态码。
      如果 code 不在这个范围（比如是业务错误码 1001），就用 400 作为 HTTP 状态码。
      这样做的目的是：HTTP 状态码始终是合法的值，不会因为业务错误码导致 HTTP 响应异常。
    """
    return JSONResponse(
        # 设置 HTTP 响应状态码。
        status_code=code if 400 <= code < 600 else 400,
        # content 是响应的 JSON 内容，格式与 ok() 一致，保持统一。
        content={"code": code, "msg": msg, "data": data},
    )


# ==================== 全局异常处理器 ====================

def add_exception_handlers(app) -> None:
    """
    注册全局异常处理器。

    这个函数接收 FastAPI 应用实例，注册三类异常处理器：
      1. HTTPException：路由中显式抛出的 HTTP 异常（如 abort(404)）。
      2. RequestValidationError：FastAPI 参数校验失败时自动抛出的异常。
      3. Exception：所有未被捕获的未知异常（兜底处理）。

    参数：
      app：FastAPI 应用实例。通过 @app.exception_handler() 装饰器
        可以注册特定异常类型的处理器。

    为什么需要全局异常处理器？
      如果不注册，不同类型的异常会返回不同格式的响应：
      - HTTPException 返回 {"detail": "Not Found"}（只有 msg，没有 code 和 data）。
      - RequestValidationError 返回一个很长的错误列表（格式很复杂）。
      - 未知异常返回 HTML 格式的错误页面（不是 JSON）。
      注册后，所有异常都会被转换成统一的 {"code": xxx, "msg": "xxx", "data": xxx} 格式。
    """

    # ==================== HTTP 异常处理器 ====================
    # 捕获 StarletteHTTPException，这是所有 HTTP 异常的基类。
    # 常见触发场景：
    #   - 路由函数中调用 raise HTTPException(status_code=404, detail="资源不存在")。
    #   - FastAPI 自动检测到的错误，比如路由不存在时返回 404。
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        # 将异常转换为统一格式的 JSON 响应。
        # status_code：HTTP 原始状态码（如 404、403、401）。
        # code：直接使用 HTTP 状态码作为业务错误码，方便前端根据 code 做判断。
        # msg：从异常的 detail 字段提取错误描述（这是 FastAPI/Starlette 的标准字段）。
        # data：对于 HTTP 异常，没有附加数据，设为 None。
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": exc.status_code, "msg": str(exc.detail), "data": None},
        )

    # ==================== 参数校验异常处理器 ====================
    # 捕获 RequestValidationError。当 FastAPI 的参数校验失败时会抛出此异常。
    # 常见触发场景：
    #   - 请求体中缺少必填字段。
    #   - 字段类型不匹配（比如该传数字却传了字符串）。
    #   - 字段值不符合约束（比如字符串太长、数字超出范围）。
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        # 默认错误信息。
        msg = "参数校验失败"

        # 获取所有校验错误的详细列表。
        # exc.errors() 返回一个列表，每个元素是一个字典，包含错误类型、位置、信息等。
        errors = exc.errors()

        if errors:
            # 取第一个错误作为主要提示信息（因为通常只需要展示一个最相关的错误）。
            first = errors[0]
            # 提取错误的位置信息。"loc" 字段是一个元组，表示出错字段的路径。
            # 例如 ("body", "username") 表示请求体中的 username 字段。
            # 用 "." 连接成字符串，并过滤掉 "body" 这个层级（因为前端知道数据来自请求体）。
            # 最终结果类似 "username" 或 "address.city"。
            loc = ".".join(str(x) for x in first.get("loc", []) if x != "body")
            # 如果有位置信息，就用 "位置: 错误描述" 的格式（如 "username: field required"）。
            # 如果没有位置信息，就直接使用错误描述。
            msg = f"{loc}: {first.get('msg', msg)}" if loc else first.get("msg", msg)

        # 返回 422 状态码（Unprocessable Entity）。
        # 422 表示"请求格式正确，但语义有问题"（比如字段类型不对）。
        # code 设为 422，与 HTTP 状态码一致。
        # data 字段返回完整的错误列表，方便前端逐个字段显示错误信息。
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"code": 422, "msg": msg, "data": exc.errors()},
        )

    # ==================== 未知异常处理器（兜底） ====================
    # 捕获所有未被上面两个处理器捕获的异常。
    # 这是最后一道防线，确保任何异常都不会返回非标准格式的响应。
    # 常见触发场景：
    #   - 数据库连接失败（ConnectionError）。
    #   - Redis 不可用。
    #   - 代码中的未预期错误（如 KeyError、AttributeError）。
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        # 返回 500 状态码（Internal Server Error）。
        # msg 中包含了异常的具体信息，方便后端排查问题。
        # 注意：在生产环境中，不建议把异常详情返回给前端（可能泄露敏感信息），
        # 但这里为了开发调试方便选择了暴露。生产环境可以改为固定提示"服务器内部错误"。
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"code": 500, "msg": f"服务器内部错误：{exc}", "data": None},
        )
