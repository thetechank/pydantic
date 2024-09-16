from pydantic import BaseModel, Field, field_validator
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import HTTPException

# from app.models.Choice import Choice
from .Choice import Choice


class PollCreate(BaseModel):
    """Poll write data model"""

    title: str = Field(min_length=5, max_length=50)
    options: List[str]
    expires_at: Optional[datetime] = None

    @field_validator("options")
    @classmethod
    def validate_options(cls, v: List[str]) -> List[str]:
        if len(v) < 2 or len(v) > 5:
            # raise ValueError("A poll must contain between 2 and 5 choices")
            raise HTTPException(
                status_code=400, detail="A poll must contain between 2 and 5 choices"
            )
        return v

    def create_poll(self) -> "Poll":
        """
        Create a new Poll instance with auto-incrementing labels for
        Choices, e.g. 1, 2, 3

        This will be used in the POST /polls/create endpoint
        """
        choices = [
            Choice(description=desc, label=index + 1)
            for index, desc in enumerate(self.options)
        ]

        if self.expires_at is not None and self.expires_at < datetime.now(timezone.utc):
            # raise ValueError("A poll's expiration must be in the future")
            raise HTTPException(
                status_code=400, detail="A poll's expiration must be in the future"
            )

        return Poll(title=self.title, options=choices, expires_at=self.expires_at)


class Poll(PollCreate):
    """Poll read data model, with uuid and creation date"""

    id: UUID = Field(default_factory=uuid4)
    options: List[Choice]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def is_active(self) -> bool:
        if self.expires_at is None:
            return True

        return datetime.now(timezone.utc) < self.expires_at
