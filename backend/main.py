from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
import torch
import os

#  Set a different cache directory (change to a larger drive path)
os.environ["HF_HOME"] = "D:/huggingface_cache"  # Change D: to your preferred location

# Clear GPU memory before loading the model
torch.cuda.empty_cache()

# Initialize BlenderBot 3 with FP16 Precision and GPU Acceleration
model_name = "facebook/blenderbot-400M-distill"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name).half().to("cuda")  # FP16 + GPU
chatbot = pipeline("text2text-generation", model=model, tokenizer=tokenizer, device=0)

app = FastAPI()

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

# POST Endpoint with Optimized Generation
@app.post("/chat")
def get_response(message: Message):
    try:
        # Generate a faster response using FP16-optimized BlenderBot 3
        response = chatbot(
    f"You are a supportive mental health assistant. Respond with empathy and clarity. User says: {message.user_message}",
        max_length=100,
        temperature=0.5,  # Lower value = less randomness
        top_p=0.8         # Limits the range of token sampling
)
         # Post-process the response for inappropriate language
        response_text = response[0]['generated_text']
        inappropriate_terms = ["fuck", "ever", "shut up", "nonsense", "steak"]
        if any(term in response_text.lower() for term in inappropriate_terms):
            response_text = "I'm here to support you with kindness and care. Please share how you're feeling."

        return {"response": response_text}
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


