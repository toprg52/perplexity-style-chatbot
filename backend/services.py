import os
import re
import asyncio
from tavily import TavilyClient
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not TAVILY_API_KEY or not GEMINI_API_KEY:
    print("Warning: API Keys missing in .env")

# Initialize Clients
try:
    tavily = TavilyClient(api_key=TAVILY_API_KEY)
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash-lite')
except Exception as e:
    print(f"Error initializing services: {e}")

def search_web(query):
    """
    Sends the user's query to Tavily and gets back the top 5 relevant results.
    """
    try:
        response = tavily.search(query=query, search_depth="advanced", max_results=5)
        return response['results']
    except Exception as e:
        print(f"Search failed: {e}")
        return []

def extract_youtube_id(url):
    """
    Extracts the video ID from a YouTube URL.
    """
    pattern = r'(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]+)'
    if match:
        return match.group(1)
    return None

def generate_search_query(history, user_input):
    """
    Uses Gemini to transform the user's input into a standalone search query
    based on the conversation history.
    """
    if not history:
        return user_input

    history_text = "\n".join([
        f"{msg['role'].title()}: {msg.get('content', '')}" 
        for msg in history[-4:] # Use last few messages for context
    ])

    prompt = f"""
    Given the following conversation history, transform the user's last question into a standalone search query that can be used to find relevant information on the web.
    If the user's question is already a standalone query, return it as is.
    Do not answer the question, just provides the best search query.
    
    Conversation History:
    {history_text}
    
    User's Last Question: {user_input}
    
    Standalone Search Query:
    """
    
    try:
        response = model.generate_content(prompt)
        # Clean up response (remove quotes, newlines)
        return response.text.strip().strip('"')
    except Exception as e:
        print(f"Query generation failed: {e}")
        return user_input

async def generate_response_stream(query, search_results, history=[]):
    """
    Generates a streaming response from Gemini.
    """
    # Create Context
    context_text = "\n\n".join([
        f"Source: {r['title']}\nURL: {r['url']}\nContent: {r['content']}"
        for r in search_results
    ])

    # Format History
    history_text = ""
    if history:
        history_text = "Conversation History:\n" + "\n".join([
            f"{msg['role'].title()}: {msg.get('content', '')}" 
            for msg in history
        ]) + "\n\n"

    prompt = f"""
    You are an expert research assistant, replicating a service like Perplexity's Comet browser.
    
    {history_text}
    User Question: {query}
    
    Here is the information found on the web:
    {context_text}
    
    Instructions:
    1. Answer the question comprehensively using ONLY the provided context.
    2. Cite your sources using [Source Name](Source URL) format within the text. Ensure every citation is a clickable markdown link.
    3. If the answer isn't in the context, state that you couldn't find it.
    4. Maintain a helpful and professional tone.
    """

    response = model.generate_content(prompt, stream=True)
    
    for chunk in response:
        if chunk.text:
            yield chunk.text
