from pydantic import BaseModel, Field
from uuid import UUID, uuid4


class ChoiceCreate(BaseModel):
    """Choice write data model, representing a single choice in a poll"""

    description: str = Field(min_length=1, max_length=100)


class Choice(ChoiceCreate):
    """Choice read model, with an a label and auto-gen uuid"""

    id: UUID = Field(default_factory=uuid4)
    label: int = Field(gt=0, lt=6)
