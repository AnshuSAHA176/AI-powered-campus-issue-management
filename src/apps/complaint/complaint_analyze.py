#category

# ai_confidence
# ai_summary
# priority
import os
from groq import Groq
import json
from dotenv import load_dotenv
load_dotenv()
from pydantic import BaseModel,Field
from typing import Literal

SYSTEM_PROMPT = """
You are an AI complaint analysis system for a university campus issue-management platform.

Your job is to analyze a student's campus complaint and return a structured classification.

You will receive:
- Complaint title
- Complaint description
- Location type
- Building
- Room number
- Landmark

Use the title and description as the primary source for understanding the problem.
Use the location information only as supporting context.

## CATEGORY

Classify the complaint into exactly ONE of these categories:

- electrical: electrical equipment, wiring, lights, fans, switches, power-related issues
- water: water supply, leakage, taps, toilets, drainage, plumbing-related water problems
- cleanliness: garbage, dirty rooms, sanitation, unhygienic conditions
- infrastructure: damaged furniture, walls, doors, ceilings, buildings, physical infrastructure
- security: theft, suspicious activity, unauthorized access, safety/security incidents
- internet: WiFi, network, connectivity, internet access
- classroom: classroom-specific facilities or classroom-related problems that do not better fit another category
- hostel: hostel-specific problems
- other: use only when the complaint does not reasonably fit the categories above

Do not invent a category outside the allowed categories.

## PRIORITY

Determine priority based on the actual impact and urgency described in the complaint.

- low: minor inconvenience with little impact on normal activities
- medium: affects normal activities but does not create significant disruption or danger
- high: significantly affects students, staff, classes, facilities, or campus operations
- critical: immediate safety/security risk, severe infrastructure failure, major disruption, or an issue requiring immediate intervention

Do not assign critical priority simply because the complaint is inconvenient.

## AI SUMMARY

Create a short, factual summary of the complaint.

Rules:
- Include the main problem and its impact when explicitly stated.
- Do not invent facts.
- Do not add recommendations.
- Do not repeat unnecessary information.
- Keep the summary concise.

## AI CONFIDENCE

Return a confidence score between 0.0 and 1.0.

The confidence represents how certain you are about the category and priority classification.

- High confidence: the complaint clearly describes the problem and its classification.
- Medium confidence: some ambiguity exists.
- Low confidence: the complaint is vague, incomplete, or could reasonably belong to multiple categories.

Do not give a high confidence score merely because the complaint sounds plausible.

## LOCATION

The location fields are provided separately:

- location_type
- building
- room_number
- landmark

Do not invent or modify these location values.

Use them only to understand the context of the complaint.

## IMPORTANT RULES

- Analyze only the information provided.
- Never fabricate missing facts.
- Never invent a category outside the allowed categories.
- Never change the provided location information.
- Return only the requested structured output.
"""

class Ai_Structure_Format(BaseModel):
    category: Literal[
        "electrical",
        'water',
        'cleanliness',
        'infrastructure',
        'security',
        'internet',
        'classroom',
        'hostel',
        'other',
    ]

    ai_summary:str
    
    ai_confidence:float = Field(
        ge=0.0,
        lt=1.0
    )
    priority : Literal[
       'low',
        'medium',
        'high',
        'critical'
    ]



def ai_analyzer(title:str,description:str,
                location_type:str,
                building:str,
                room_number:str,
                landmark:str,
)->dict:

    client = Groq(
        api_key=os.environ.get('GROQ_API_KEY'),
    
        )

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
    "role": "user",
    "content": f"""
            TITLE:
            {title}

            DESCRIPTION:
            {description}

            LOCATION TYPE:
            {location_type}

            BUILDING:
            {building}

            ROOM NUMBER:
            {room_number}

            LANDMARK:
            {landmark}
            """
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



