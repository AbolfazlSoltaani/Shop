import openai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")


def get_openai_response(messages):
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    return response["choices"][0]["message"]["content"]
