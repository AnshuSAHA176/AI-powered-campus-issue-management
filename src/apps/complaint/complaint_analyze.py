#category

# ai_confidence
# ai_summary
# priority
import os
from groq import Groq
import json
from dotenv import load_dotenv
load_dotenv()
from pydantic import BaseModel,AfterValidator
from typing import Literal,Annotated
SYSTEM_PROMPT = """
You are an AI complaint analysis system for a university campus issue-management platform.

Your task is to analyze a student's complaint using ONLY the provided title and description.

Extract and classify the complaint into the required structured fields:

1. category:
   - Identify the main type of campus issue.
   - Choose the most appropriate category based on the actual problem described.
   - Do not invent information that is not present.

2. priority:
   - low: minor issue with little immediate impact.
   - medium: issue affecting normal activities but not causing serious disruption.
   - high: significant issue affecting students, staff, classes, facilities, or campus operations.
   - critical: immediate safety risk, major infrastructure failure, severe security issue, or problem requiring urgent intervention.

3. ai_summary:
   - Write a concise, factual summary of the complaint.
   - Do not add information that is not supported by the title or description.

4. ai_confidence:
   - Return a value between 0.0 and 1.0.
   - Represent how confident you are in your classification.
   - Use a lower confidence when the complaint is vague, ambiguous, or missing important information.
   - Do not use high confidence simply because the complaint sounds plausible.

Important rules:
- Do not fabricate missing details.
- Do not assume facts that are not stated.
- Prioritize the actual impact and urgency described by the student.
- Return only the requested structured output.
"""

class Ai_Structure_Format(BaseModel):
    category: Literal[
        "electrical",
        'water'
        'cleanliness'
        'infrastructure'
        'security'
        'internet'
        'classroom'
        'hostel'
        'other'
    ]

    ai_summary:str
    
    ai_confidence:float
    priority : Literal[
       'low',
        'medium',
        'high',
        'critical'
    ]



def ai_analyzer(title:str,description:str)->dict:

    client = Groq(
        api_key=os.environ.get('GROQ_API_KEY'),
    
        )

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"TITLE:- {title} , DESCRIPTION:- {description}",
            },
        ],
        response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "support_ticket_classification",
            "schema": Ai_Structure_Format.model_json_schema()
        }
    }
    )

    result = Ai_Structure_Format.model_validate(
        json.loads(response.choices[0].message.content or "{}")
        )
    return result.model_dump()



