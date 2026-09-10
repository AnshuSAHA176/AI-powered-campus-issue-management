from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
load_dotenv()





def get_model(model="openai/gpt-oss-120b"):
    return ChatGroq(
        model=model,
        temperature=0,
        max_retries=2,
    )
