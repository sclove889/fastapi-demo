from typing import Any

from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse


def success_response(message: str = "success", data: Any = None):
    context = {
        "code": 200,
        "message": message ,
        "data": data
    }

    return JSONResponse(jsonable_encoder(context))