import os
import logging
import sqlite3
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

# CORS middleware (optional, adjust as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database path
DB_PATH = "knowledge_base.db"

# Pydantic model for queries
class QueryRequest(BaseModel):
    question: str
    # Add other fields if needed

async def query_knowledge_base(request: QueryRequest):
    # Your actual answer logic here
    answer = f"Received question: {request.question}"
    links = []  # Or provide actual relevant links if you have them
    return {"answer": answer, "links": links}

# /query endpoint
@app.post("/query")
async def query_endpoint(request: QueryRequest):
    return await query_knowledge_base(request)

# Root POST endpoint (acts like /query)
@app.post("/")
async def root_post(request: Request):
    data = await request.json()
    try:
        query_req = QueryRequest(**data)
    except ValidationError as e:
        return {"error": "Invalid request", "details": e.errors()}
    return await query_knowledge_base(query_req)

# /health endpoint
@app.get("/health")
def health():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM discourse_chunks")
        discourse_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM markdown_chunks")
        markdown_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM discourse_chunks WHERE embedding IS NOT NULL")
        discourse_embeddings = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM markdown_chunks WHERE embedding IS NOT NULL")
        markdown_embeddings = cursor.fetchone()[0]
        conn.close()
        return {
            "status": "healthy",
            "database": "connected",
            "api_key_set": bool(API_KEY),
            "discourse_chunks": discourse_count,
            "markdown_chunks": markdown_count,
            "discourse_embeddings": discourse_embeddings,
            "markdown_embeddings": markdown_embeddings
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "api_key_set": bool(API_KEY)
        }
    