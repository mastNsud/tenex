import os
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from groq import Groq
import logging
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from models import Base

# ... (logging setup)

app = FastAPI(
    title="Tenex Tutorials API",
    docs_url="/docs" if os.getenv("ENV") == "development" else None
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Database Setup
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    logger.error("DATABASE_URL not found! Please set it in Railway Variables.")
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

@app.on_event("startup")
async def startup():
    if engine:
        async with engine.begin() as conn:
            # Create tables if they don't exist
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created/verified.")

async def get_db():
    if not AsyncSessionLocal:
        raise HTTPException(status_code=500, detail="Database not configured")
    async with AsyncSessionLocal() as session:
        yield session

# Groq AI Client
# ... (groq init)

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    logger.info("Root endpoint hit - serving frontend")
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    return {"status": "healthy", "env": os.getenv("ENV"), "db_connected": engine is not None}

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
