from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

from database import create_session, get_sessions, get_session, add_message, update_session_title, delete_session
from services import search_web, generate_response_stream, generate_search_query

app = FastAPI()

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class ChatRequest(BaseModel):
    session_id: str
    message: str

class SessionCreate(BaseModel):
    title: str = "New Chat"

# Routes

@app.get("/")
async def root():
    return {"status": "ok", "service": "Perplexity Cone Backend"}

@app.get("/api/sessions")
async def list_sessions():
    return await get_sessions()

@app.post("/api/sessions")
async def create_new_session(session: SessionCreate):
    data = {
        "title": session.title,
        "created_at": datetime.utcnow(),
        "messages": []
    }
    return await create_session(data)

@app.get("/api/sessions/{session_id}")
async def get_session_history(session_id: str):
    session = await get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@app.patch("/api/sessions/{session_id}")
async def update_session_title_endpoint(session_id: str, payload: dict = Body(...)):
    new_title = payload.get("title")
    if not new_title:
        raise HTTPException(status_code=400, detail="Title is required")
    await update_session_title(session_id, new_title)
    return {"status": "ok", "title": new_title}

@app.delete("/api/sessions/{session_id}")
async def delete_session_endpoint(session_id: str):
    success = await delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "ok"}

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    session_id = request.session_id
    user_query = request.message
    
    # Verify session exists
    session = await get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # 1. Save User Message
    user_msg = {"role": "user", "content": user_query}
    await add_message(session_id, user_msg)
    
    # 2. Contextualize Search Query
    # Use the session messages (which represents history BEFORE this new message if fetched early, 
    # but we just added a message? No, 'session' var is stale, which is good for history)
    refined_query = generate_search_query(session['messages'], user_query)
    print(f"Refined Query: {refined_query}")
    
    # 3. Search Web with Refined Query
    search_results = search_web(refined_query)
    
    # 3. Update Title if it's the first message
    if len(session['messages']) == 0:
        new_title = " ".join(user_query.split()[:5])
        await update_session_title(session_id, new_title)

    # 4. Generator function for Streaming Response
    async def response_generator():
        full_text = ""
        # Send search results first as a special event or just part of the stream?
        # For simplicity, we'll just stream the text. 
        # But we need to save the final answer to DB.
        
        # We can send a JSON header with sources first?
        # To keep it simple, we will stream the text, and the frontend will handle sources if we return them separately?
        # StreamingResponse expects bytes or strings.
        
        # Let's send sources as a JSON line first, then the text?
        # Or standard Server Sent Events (SSE). 
        # For this "simple" migration, let's just stream text. 
        # BUT we need to send sources to the frontend.
        # Strategy: Send a JSON object with sources as the first chunk?
        # Or use a special separator.
        
        # Let's format the first chunk as JSON containing sources.
        import json
        sources_data = json.dumps({"type": "sources", "data": search_results}) + "\n--split--\n"
        yield sources_data
        
        try:
            # Stream Gemini content
            async for chunk in generate_response_stream(user_query, search_results, session['messages']):
                full_text += chunk
                yield chunk

            # Save Assistant Message to DB
            assistant_msg = {
                "role": "assistant",
                "content": full_text,
                "sources": search_results
            }
            await add_message(session_id, assistant_msg)
        except Exception as e:
            print(f"Streaming Error: {e}")
            yield f"\n\n[System Error: An unexpected error occurred during generation.]"

    return StreamingResponse(response_generator(), media_type="text/plain")

if __name__ == "__main__":
    print("DEBUG: Entered __main__")
    import uvicorn
    import logging
    print("DEBUG: Imports done")

    # Configure file logging
    logging.basicConfig(filename='server_lifecycle.log', level=logging.DEBUG)
    print("DEBUG: Logging configured")
    logging.info("Starting Server on Port 8005...")
    
    try:
        print("DEBUG: Starting Uvicorn run...")
        uvicorn.run(app, host="0.0.0.0", port=8005)
        print("DEBUG: Uvicorn run finished (clean exit)")
    except Exception as e:
        print(f"DEBUG: Server crashed with exception: {e}")
        logging.critical(f"Server crashed: {e}")
    print("DEBUG: End of script")
