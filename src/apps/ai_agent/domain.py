from typing import Literal
from pydantic import BaseModel
import json

from .llm import get_model


class Domain(BaseModel):
    domain: Literal["campus", "unknown"]


def domain(message: str) -> str:

    model = get_model()

    prompt = f"""
You are a domain classifier for CivicAI.

Classify the user's message into exactly one of these domains:

campus
unknown

Use "campus" when the message is related to:
- campus
- university
- college
- students
- complaints
- hostels
- classrooms
- buildings
- facilities
- officers
- CivicAI

Use "unknown" for anything unrelated.

Return ONLY valid JSON.

The JSON must have exactly this structure:

{{"domain": "campus"}}

or

{{"domain": "unknown"}}

User message:
{message}
"""

    response = model.invoke(prompt)

    data = json.loads(response.content)

    result = Domain.model_validate(data)

    print(result)

    return result.domain