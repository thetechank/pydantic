from app.models.Polls import Poll
from app.models.Votes import Vote
from app.models.Results import PollResults, Result
from upstash_redis import Redis
from dotenv import load_dotenv
from uuid import UUID
from typing import Optional, List, Dict
import os

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")
REDIS_TOKEN = os.getenv("REDIS_TOKEN")

redis_client = Redis(url=REDIS_URL, token=REDIS_TOKEN)


def save_poll(poll: Poll) -> None:
    poll_json = poll.model_dump_json()
    redis_client.set(f"poll:{poll.id}", poll_json)


def get_poll(poll_id: UUID) -> Optional[Poll]:
    poll_json = redis_client.get(f"poll:{poll_id}")

    if poll_json:
        return Poll.model_validate_json(poll_json)

    return None


def get_all_polls() -> List[Poll]:
    poll_keys = redis_client.keys("poll:*")

    # polls = []

    # for key in poll_keys:
    #     poll_json = redis_client.get(key)
    #     if poll_json:
    #         polls.append(Poll.model_validate_json(poll_json))

    poll_jsons = redis_client.mget(*poll_keys)
    # redis_client.mget(poll_id_1, poll_id_2, poll_id_3, ...)

    polls = [Poll.model_validate_json(pj) for pj in poll_jsons if pj]

    return polls


def get_choice_id_by_label(poll_id: UUID, label: int) -> Optional[UUID]:
    poll = get_poll(poll_id)

    return get_choice_id_by_label_given(poll, label)


def get_choice_id_by_label_given(poll: Poll, label: int) -> Optional[UUID]:
    if not poll:
        return None

    for choice in poll.options:
        if choice.label == label:
            return choice.id

    return None


def get_vote(poll_id: UUID, email: str) -> Optional[Vote]:
    vote_json = redis_client.hget(f"votes:{poll_id}", email)

    if vote_json:
        return Vote.model_validate_json(vote_json)

    return None


def save_vote(poll_id: UUID, vote: Vote) -> None:
    vote_json = vote.model_dump_json()
    redis_client.hset(f"votes:{poll_id}", vote.voter.email, vote_json)
    redis_client.hincrby(f"votes_count:{poll_id}", str(vote.choice_id), 1)


def get_vote_count(poll_id: UUID) -> Dict[UUID, int]:
    vote_counts = redis_client.hgetall(f"votes_count:{poll_id}")

    return {UUID(choice_id): int(count) for choice_id, count in vote_counts.items()}


def get_poll_results(poll_id: UUID) -> Optional[PollResults]:
    poll = get_poll(poll_id)
    if not poll:
        return None

    vote_counts = get_vote_count(poll_id)
    total_votes = sum(vote_counts.values())

    results = [
        Result(description=choice.description, vote_count=vote_counts.get(choice.id, 0))
        for choice in poll.options
    ]

    results = sorted(results, key=lambda x: x.vote_count, reverse=True)

    return PollResults(title=poll.title, total_votes=total_votes, results=results)


def delete_poll(poll_id: UUID) -> None:
    # redis_client(f"poll:{poll_id}")
    # redis_client(f"votes:{poll_id}")
    # redis_client(f"votes_count:{poll_id}")

    keys_to_delete = [f"poll:{poll_id}", f"votes:{poll_id}", f"votes_count:{poll_id}"]

    redis_client.delete(*keys_to_delete)
