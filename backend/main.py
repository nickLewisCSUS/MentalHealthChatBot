import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer
from better_profanity import profanity
import torch
import os
import asyncio
from slowapi import Limiter
from slowapi.util import get_remote_address

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Set cache directory (change to a larger drive path)
os.environ["HF_HOME"] = "D:/huggingface_cache"

# Clear GPU memory before loading the model
torch.cuda.empty_cache()

# Initialize BlenderBot 3 with GPU acceleration
model_name = "facebook/blenderbot-400M-distill"
device = "cuda" if torch.cuda.is_available() else "cpu"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(device)

chatbot = pipeline(
    "text2text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=100,
    temperature=0.5,
    top_p=0.8,
    repetition_penalty=1.15,
    do_sample=True,  # Fix warning
)

app = FastAPI()
context_history = []
MAX_HISTORY = 10  # Limit conversation memory

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, restrict to ["http://localhost:8000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define Message Model
class Message(BaseModel):
    user_message: str

import asyncio

@app.post("/chat")
@limiter.limit("5/minute")  # 5 messages per minute per user
async def get_response(message: Message):  # Make function async
    try:
        logging.info(f"User input: {message.user_message}")  # Log user input

        global context_history
        context_history.append({"user": message.user_message})

        # Limit history to last MAX_HISTORY messages
        context_history = context_history[-MAX_HISTORY:]

        # Convert history into formatted prompt
        conversation_history = "\n".join(
            [f"User: {msg['user']}" if 'user' in msg else f"Bot: {msg['bot']}" for msg in context_history]
        )

        formatted_input = (
            f"You are a supportive mental health assistant. Respond with empathy and clarity.\n{conversation_history}"
        )

        # Run chatbot asynchronously 
        response = await asyncio.to_thread(
            chatbot, formatted_input, max_new_tokens=100
        )

        response_text = response[0].get("generated_text", "I'm here to help. Can you tell me more?").strip()

        # Log chatbot response
        logging.info(f"Chatbot response: {response_text}")

        # Add response to history
        context_history.append({"bot": response_text})

        # Filter profanity
        if profanity.contains_profanity(response_text):
            response_text = "I'm here to provide emotional support. Please share how you're feeling."

        return {"response": response_text}

    except Exception as e:
        logging.error(f"Error: {e}", exc_info=True)  # Log error with traceback
        return HTTPException(status_code=500, detail=f"Server error: {str(e)}")

