from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


def custom_validation_exception_handler(request: Request, exc: RequestValidationError):
    exceptions = exc.errors()

    if len(exceptions) == 1:
        # return JSONResponse(
        # status_code=422, content={"detail": exceptions[0]["msg"].capitalize()}
        # )

        # or to also show the offending field:
        return JSONResponse(
            status_code=422,
            content={
                "detail": f"{'.'.join(exceptions[0]['loc'])}: {exceptions[0]['msg'].capitalize()}"
            },
        )
    else:
        return JSONResponse(
            status_code=422, content={"detail": [error["msg"] for error in exceptions]}
        )
