import os
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from groq import Groq
import logging
from pythonjsonlogger import jsonlogger

# Load environment variables
load_dotenv()

# Setup logging
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

app = FastAPI(
    title="Tenex Tutorials API",
    docs_url="/docs" if os.getenv("ENV") == "development" else None
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Update with frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Setup
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    logger.error("DATABASE_URL not found! Please set it in Railway Variables.")
    # For now, we'll initialize a dummy engine or raise a clearer error
    # raise ValueError("DATABASE_URL is missing")
    engine = None
    AsyncSessionLocal = None
else:
    engine = create_async_engine(
        DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True
    )
    AsyncSessionLocal = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

async def get_db():
    if AsyncSessionLocal is None:
        raise HTTPException(
            status_code=503,
            detail="Database not configured (DATABASE_URL is missing)"
        )
    async with AsyncSessionLocal() as session:
        yield session

# Groq AI Client
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    logger.error("GROQ_API_KEY not found! AI features will be disabled.")
    groq_client = None
else:
    groq_client = Groq(api_key=GROQ_API_KEY)

@app.get("/")
async def root():
    logger.info("Root endpoint hit - version 1.0.1")
    return {
        "message": "Welcome to Tenex Tutorials API 🎓",
        "version": "1.0.1",
        "docs": "/docs (dev only)",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "env": os.getenv("ENV"),
        "database": "connected" if engine is not None else "unavailable (DATABASE_URL not set)",
    }

@app.post("/api/chat")
async def chat(message: str, current_user_id: int = None):
    if not groq_client:
        raise HTTPException(status_code=503, detail="AI Service not configured (missing API key)")
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a helpful math and science tutor for Indian Class 10 students (CBSE/ICSE)."},
                {"role": "user", "content": message}
            ],
            max_tokens=500,
            temperature=0.7
        )
        ai_response = response.choices[0].message.content
        
        # In a real app, you'd save this to ChatLog here
        logger.info("AI Chat Response", extra={
            "user_id": current_user_id,
            "message": message,
            "response": ai_response
        })
        
        return {"response": ai_response}
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail="AI Service currently unavailable")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, workers=1)
