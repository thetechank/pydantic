from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from app.api import polls, votes, danger, exceptions


app = FastAPI(
    title="Polls API",
    description="A simple API to create and vote on polls",
    version="0.1",
    openapi_tags=[
        {
            "name": "polls",
            "description": "Operations related to creating and viewing polls",
        },
        {
            "name": "danger",
            "description": "Operations that lead to irreversible data loss",
        },
        {
            "name": "votes",
            "description": "Operations related to casting votes",
        },
    ],
)


app.add_exception_handler(
    RequestValidationError, exceptions.custom_validation_exception_handler
)
app.include_router(polls.router, prefix="/polls", tags=["polls"])
app.include_router(danger.router, prefix="/polls", tags=["danger"])
app.include_router(votes.router, prefix="/vote", tags=["votes"])


# Objective:
# - reshape the pydantic error messages into custom messages that only
# include the "msg" property of the error
