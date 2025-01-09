import openai
from dotenv import load_dotenv
import os

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# List available models for the API key
models = client.models.list()
for model in models.data:
    print(model.id)
