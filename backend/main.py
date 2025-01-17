from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer
from better_profanity import profanity
import torch
import os

#  Set a different cache directory (change to a larger drive path)
os.environ["HF_HOME"] = "D:/huggingface_cache"  # Change D: to your preferred location

# Clear GPU memory before loading the model
torch.cuda.empty_cache()

# Initialize BlenderBot 3 with FP16 Precision and GPU Acceleration
model_name = "facebook/blenderbot-400M-distill"

tokenizer = AutoTokenizer.from_pretrained(model_name)

model = AutoModelForSeq2SeqLM.from_pretrained(model_name).half().to("cuda")  # FP16 + GPU

chatbot = pipeline("text2text-generation", model=model, tokenizer=tokenizer, max_new_tokens=1024, temperature=0, top_p=0.95, repetition_penalty=1.15)

app = FastAPI()
context_history = []

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, restrict this to ["http://localhost:8000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define Message Model
class Message(BaseModel):
    user_message: str

@app.post("/chat")
def get_response(message: Message):
    try:
        global context_history
        context_history.append(f"User: {message.user_message}")

        # Limit the context history to the last 10 messages
        if len(context_history) > 10:
            context_history.pop(0)

        # Combine context history into a single string
        conversation_history = "\n".join(context_history)

        formatted_input = (
            f"You are a supportive mental health assistant. Respond with empathy and clarity.\n{conversation_history}"
        )


        # Generate response
        response = chatbot(
            formatted_input,
            max_new_tokens=100,
            temperature=0.5,
            top_p=0.8,
        )

        print("Raw response:", response)

        # Extract the generated text
        response_text = response[0].get("generated_text", "I'm here to help. Can you tell me more?")
        response_text = response_text.strip()

        # Add the bot's response to the context history
        context_history.append(f"Bot: {response_text}")

        # Filter profanity in the response
        if profanity.contains_profanity(response_text):
            response_text = "I'm here to provide emotional support. Please share how you're feeling."

        return {"response": response_text}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

