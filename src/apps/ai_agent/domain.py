from typing import Literal
from pydantic import BaseModel

from .llm import get_model


class Domain(BaseModel):
    domain: Literal["campus", "unknown"]


def domain(message: str) -> str:

    model = get_model().with_structured_output(Domain)

    prompt = f"""
You are a domain classifier for CivicAI.

Determine whether the user's message is related to a
campus/university system.

Return:
- campus → campus, university, students, complaints, hostels,
  classrooms, buildings, facilities, officers, or CivicAI.
- unknown → anything unrelated to the campus.

User message:
{message}
"""

    result = model.invoke(prompt)

    return result.domain