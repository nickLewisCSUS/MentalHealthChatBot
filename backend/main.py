# backend/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# Define a message model for conversation data
class Message(BaseModel):
    user_message: str

@app.post("/chat")
def get_response(message: Message):
    try:
        # Call OpenAI's API for emotional support responses
        response = openai.Completion.create(
            engine="text-davinci-003",  
            prompt=f"You are an empathetic mental health support assistant. Respond to: {message.user_message}",
            max_tokens=150
        )
        return {"response": response.choices[0].text.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))