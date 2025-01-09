# backend/main.py (using Hugging Face)
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import pipeline

# Initialize the Hugging Face model
chatbot = pipeline("text2text-generation", model="google/flan-t5-large")

app = FastAPI()

class Message(BaseModel):
    user_message: str

@app.post("/chat")
def get_response(message: Message):
    try:
        # Generate a response using the Hugging Face model
        response = chatbot(f"You are a supportive mental health assistant. User says: {message.user_message}", max_length=100)
        return {"response": response[0]['generated_text']}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")