import os
from dotenv import load_dotenv
from autogen_ext.models.openai import OpenAIChatCompletionClient

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")


def get_model_client():
    return OpenAIChatCompletionClient(
        model=MODEL_NAME,
        api_key=OPENAI_API_KEY
    )