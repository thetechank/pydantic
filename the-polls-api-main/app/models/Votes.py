from pydantic import BaseModel, Field, EmailStr
from uuid import UUID
from datetime import datetime


class VoterCreate(BaseModel):
    """The Voter write model, consisting of only email address"""

    email: EmailStr


class Voter(VoterCreate):
    """The Voter read model"""

    voted_at: datetime = Field(default_factory=datetime.now)


class Vote(BaseModel):
    """The Vote read model"""

    poll_id: UUID
    choice_id: UUID
    voter: Voter


class VoteById(BaseModel):
    choice_id: UUID
    voter: VoterCreate


class VoteByLabel(BaseModel):
    choice_label: int
    voter: VoterCreate
