import streamlit as st
import os
import time
import uuid
from dotenv import load_dotenv
from tavily import TavilyClient
import google.generativeai as genai

# --- 1. SETUP, SECURITY, AND RATE LIMIT TRACKING ---

# Load environment variables from the .env file
load_dotenv()

# Get keys from the environment (not hardcoded!)
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Define the mandatory delay based on the free tier limit (5 RPM for Pro/Flash, up to 15 RPM for Lite)
# We use 15 seconds to be very safe against 429s
REQUIRED_DELAY = 15

# Initialize the last search time tracker in Streamlit's session state
if 'last_search_time' not in st.session_state:
    st.session_state.last_search_time = 0 

# Check if keys are missing
if not TAVILY_API_KEY or not GEMINI_API_KEY:
    st.error("🚨 API keys are missing! Please create a .env file with your keys.")
    st.stop()

# Initialize the Clients
try:
    tavily = TavilyClient(api_key=TAVILY_API_KEY)
    genai.configure(api_key=GEMINI_API_KEY)
    # Using 'gemini-2.5-flash-lite' as requested
    model = genai.GenerativeModel('gemini-2.5-flash-lite')
except Exception as e:
    st.error(f"Error initializing services. Check your keys. Details: {e}")
    st.stop()


# --- 2. BACKEND FUNCTIONS ---

def search_web(query):
    """
    Sends the user's query to Tavily and gets back the top 5 relevant results.
    We use 'advanced' depth for better quality.
    """
    try:
        response = tavily.search(query=query, search_depth="advanced", max_results=5)
        return response['results']
    except Exception as e:
        st.error(f"Search failed: {e}")
        return []

def generate_answer(query, search_results, history=[]):
    """
    Feeds the search results and conversation history into Gemini to write a summary.
    Arguments:
        query: User's current question
        search_results: List of sources from Tavily
        history: List of previous messages (st.session_state.messages)
    """
    # Create a string containing all the search data (The RAG Context)
    context_text = "\n\n".join([
        f"Source: {r['title']}\nURL: {r['url']}\nContent: {r['content']}"
        for r in search_results
    ])

    # Format history for the prompt
    history_text = ""
    if history:
        history_text = "Conversation History:\n" + "\n".join([
            f"{msg['role'].title()}: {msg.get('plain_text', msg['content'])}" 
            for msg in history
        ]) + "\n\n"

    # The prompt tells Gemini how to behave
    prompt = f"""
    You are an expert research assistant, replicating a service like Perplexity's Comet browser.
    
    {history_text}
    User Question: {query}
    
    Here is the information found on the web:
    {context_text}
    
    Instructions:
    1. Answer the question comprehensively using ONLY the provided context.
    2. Cite your sources using [Source Name] format within the text.
    3. If the answer isn't in the context, state that you couldn't find it.
    4. Maintain a helpful and professional tone.
    """
    
    # Enable streaming
    response = model.generate_content(prompt, stream=True)
    return response

# --- 3. FRONTEND UI (Streamlit) ---

st.set_page_config(page_title="Exponentia.ai Search", page_icon="fq", layout="wide", initial_sidebar_state="expanded")

# --- CUSTOM CSS & BRANDING ---
st.markdown("""
<style>
    /* Import Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }

    /* Main Background & Colors */
    .stApp {
        background-color: #ffffff;
        color: #1f1f1f;
    }

    /* Header Styling */
    .main-header {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 1rem 0;
        margin-bottom: 2rem;
    }
    
    /* Gradient Text for Gemini Feel */
    .brand-text {
        font-size: 1.8rem;
        font-weight: 700;
        letter-spacing: -0.5px;
        color: #444;
    }
    
    .gemini-header {
        font-size: 3.5rem;
        font-weight: 500;
        background: linear-gradient(to right, #4285F4, #9B72CB, #D96570);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .gemini-subtext {
        color: #6b7280; 
        font-size: 1.5rem; 
        margin-bottom: 3rem;
        font-weight: 300;
    }

    /* Input Styling - Minimalist Floating Pill */
    .stTextInput > div > div > input {
        border-radius: 24px;
        padding: 15px 25px;
        border: 1px solid #dfe1e5;
        background-color: #f0f4f9; /* Light Gemini Gray */
        transition: all 0.2s ease;
        font-size: 1rem;
        color: #1f1f1f;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #dfe1e5;
        background-color: white;
        box-shadow: 0 1px 6px rgba(32, 33, 36, 0.28);
    }

    /* Source Card Styling (Compact Pill-like Cards) */
    .source-card {
        background: #f0f4f9;
        padding: 0.8rem 1rem;
        border-radius: 18px; /* Rounder */
        border: none;
        width: 100%;
        height: 100%;
        transition: all 0.2s;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        text-decoration: none;
    }
    
    .source-card:hover {
        background: #e2e7eb;
        transform: translateY(-2px);
    }
    
    .source-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #1f1f1f;
        margin-bottom: 0.3rem;
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        line-height: 1.3;
    }
    
    .source-url {
        font-size: 0.7rem;
        color: #5f6368;
        display: flex;
        align-items: center;
        gap: 0.25rem;
    }

    /* Answer Section */
    .answer-box {
        margin-top: 1.5rem;
        padding-top: 0;
        font-size: 1.05rem;
        line-height: 1.7;
        color: #1f1f1f;
    }
    
    /* Header for Answer/Sources */
    .section-header {
        font-size: 0.9rem;
        font-weight: 600;
        color: #5f6368;
        margin-bottom: 0.8rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Suggestions Grid (Pill Cards) */
    .suggestion-card {
        background: #f0f4f9;
        padding: 1.2rem;
        border-radius: 16px;
        height: 100%;
        cursor: pointer;
        transition: all 0.2s;
        color: #1f1f1f;
        font-weight: 500;
        display: flex;
        align-items: flex-start;
        font-size: 0.95rem;
    }
    
    .suggestion-card:hover {
        background: #dde3ea;
    }
    
    /* Chat Message Styling */
    .chat-user {
        background-color: #f0f4f9; /* Light Gemini Gray */
        padding: 1rem 1.5rem;
        border-radius: 24px 24px 4px 24px; /* Pill with tail */
        color: #1f1f1f;
        font-weight: 400;
        display: inline-block;
        margin: 1rem 0;
        max-width: 80%;
    }
    
    /* Hide Streamlit Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    /* header {visibility: hidden;} */
    
    /* Make sidebar consistent and hide close button to feel "permanent" */
    [data-testid="stSidebar"] {
        min-width: 300px;
    }
    [data-testid="stSidebarCollapsedControl"] {
        display: none; /* Hide the collapse button */
    }
    
    /* Sticky Header in Main Chat */
    .sticky-header {
        position: sticky;
        top: 0;
        z-index: 999;
        background: white;
        padding: 1rem 0;
        border-bottom: 1px solid #f0f0f0;
        margin-bottom: 1rem;
    }
    
</style>
""", unsafe_allow_html=True)

# --- Session State Initialization (Multi-Session) ---
if "chats" not in st.session_state:
    st.session_state.chats = {} # { session_id: { 'title': '...', 'messages': [] } }

if "current_session_id" not in st.session_state:
    # Create first session
    new_id = str(uuid.uuid4())
    st.session_state.chats[new_id] = {'title': 'New Chat', 'messages': []}
    st.session_state.current_session_id = new_id

# Helper to switch chat
def switch_chat(chat_id):
    st.session_state.current_session_id = chat_id

# Helper to create new chat
def create_new_chat():
    new_id = str(uuid.uuid4())
    st.session_state.chats[new_id] = {'title': 'New Chat', 'messages': []}
    st.session_state.current_session_id = new_id

# --- Sidebar / Controls ---
with st.sidebar:
    # Sidebar branding (kept for consistency, but user also wants top layer)
    st.markdown('<div class="brand-text" style="font-size: 1.2rem; margin-bottom: 1rem;">exponentia<span style="color:#4285F4">.ai</span></div>', unsafe_allow_html=True)
    
    if st.button("New Chat", type="primary", icon="➕", use_container_width=True):
        create_new_chat()
        st.rerun()
    
    # Recent Chats List
    st.markdown('<div style="margin-bottom: 0.5rem; font-size: 0.85rem; font-weight: 600; color: #5f6368;">My Chats</div>', unsafe_allow_html=True)
    
    chat_ids = list(st.session_state.chats.keys())[::-1]
    
    for c_id in chat_ids:
        chat_data = st.session_state.chats[c_id]
        title = chat_data['title']
        
        if c_id == st.session_state.current_session_id:
             st.markdown(f"""
            <div style="background-color: #d3e3fd; color: #001d35; border-radius: 50px; padding: 8px 16px; margin-bottom: 4px; font-size: 0.9rem; font-weight: 500; cursor: default;">
                {title}
            </div>
            """, unsafe_allow_html=True)
        else:
            if st.button(title, key=c_id, use_container_width=True):
                switch_chat(c_id)
                st.rerun()

    st.markdown("---")
    st.caption("Powered by Gemini 2.0 Flash Lite & Tavily")

# --- Top Layer Branding ---
st.markdown("""
    <div class="sticky-header">
        <div class="brand-text" style="font-size: 1.5rem;">exponentia<span style="color:#4285F4">.ai</span></div>
    </div>
""", unsafe_allow_html=True)

# --- Logic for Current Session ---
current_chat = st.session_state.chats[st.session_state.current_session_id]
current_messages = current_chat['messages']

# --- Landing Page (Empty State for Current Session) ---
if not current_messages:
    # Centered Landing Layout
    st.markdown("""
    <div style="display: flex; flex-direction: column; align-items: flex-start; justify-content: center; height: 35vh; max-width: 800px; margin: 0 auto;">
        <div class="gemini-header">Hello, Human</div>
        <div class="gemini-subtext">How can I help you today?</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Suggestion Cards
    cols = st.columns(4)
    suggestions = [
        "Create a workout plan",
        "Python script for SEO",
        "Explain Quantum Physics",
        "Trends in AI Agents"
    ]
    
    for i, col in enumerate(cols):
        with col:
            # CLICK HANDLER FIX: Append to session state and RERUN immediately
            if st.button(suggestions[i], key=f"sugg_{i}", use_container_width=True):
                current_messages.append({"role": "user", "content": suggestions[i]})
                # Auto-title on first message
                st.session_state.chats[st.session_state.current_session_id]['title'] = suggestions[i][:30] + "..."
                st.rerun()

# --- Display History ---
for msg in current_messages:
    if msg["role"] == "user":
        st.markdown(f"""
        <div style="display: flex; justify-content: flex-end;">
            <div class="chat-user">
                {msg['content']}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(msg['content'], unsafe_allow_html=True)

# --- Search Input ---
user_query_input = st.chat_input("Message Exponentia AI...")

# 1. Handle New Input
if user_query_input:
    # Update Title if First Message
    if not current_messages:
        title_text = " ".join(user_query_input.split()[:5])
        st.session_state.chats[st.session_state.current_session_id]['title'] = title_text
        
    current_messages.append({"role": "user", "content": user_query_input})
    st.rerun() # Force rerun to update UI with user message before generating

# 2. Main Logic: Check if Last Message is USER (and needs an answer)
if current_messages and current_messages[-1]["role"] == "user":
    
    last_user_query = current_messages[-1]["content"]

    # Rate Limit Handling (Auto-Wait)
    time_since_last_search = time.time() - st.session_state.last_search_time
    
    if time_since_last_search < REQUIRED_DELAY:
        remaining_time = REQUIRED_DELAY - int(time_since_last_search) + 1
        with st.status(f"Generating... might take few seconds ({remaining_time}s)...", expanded=False) as status:
            time.sleep(remaining_time)
            status.update(label="Ready!", state="complete", expanded=False)
            
    # Execution
    status_container = st.empty()
    status_container.status("Searching web...", expanded=True)
    
    try:
        results = search_web(last_user_query)
        status_container.empty()
        
        if results:
            # Sources Layout
            sources_html_accum = "" 
            
            st.markdown('<div class="section-header"><span>🔗</span> Sources</div>', unsafe_allow_html=True)
            
            cols = st.columns(len(results) if len(results) < 4 else 4)
            for i, res in enumerate(results[:4]):
                with cols[i]:
                    st.markdown(f"""
                    <a href="{res['url']}" target="_blank" class="source-card">
                        <div class="source-title">{res['title']}</div>
                        <div class="source-url">
                            <img src="https://www.google.com/s2/favicons?domain={res['url']}" width="16" height="16" style="margin-right:5px; opacity:0.7;">
                            {res['url'].split('/')[2].replace('www.','')}
                        </div>
                    </a>
                    """, unsafe_allow_html=True)
                    
                    sources_html_accum += f"""<a href="{res['url']}" target="_blank" style="text-decoration:none; color:inherit;"><div style="background: #f9fafb; padding: 10px; border-radius: 8px; border: 1px solid #e5e7eb; width: 220px; display:inline-block; margin-right:10px; vertical-align:top;"><div style="font-weight:600; font-size:0.9rem; margin-bottom:5px; height:2.6em; overflow:hidden;">{res['title']}</div><div style="font-size:0.75rem; color:#6b7280;">{res['url'].split('/')[2]}</div></div></a>"""

            # Generate Answer
            st.markdown('<div class="section-header" style="margin-top: 1.5rem;"><span style="font-size: 1.2rem; margin-right: 5px;">✨</span> Answer</div>', unsafe_allow_html=True)
            answer_placeholder = st.empty()
            full_response_text = ""
            
            # Pass all previous messages except the very last one (which is the current prompt)
            stream = generate_answer(last_user_query, results, current_messages[:-1])
            
            for chunk in stream:
                full_response_text += chunk.text
                answer_placeholder.markdown(full_response_text)
            
            final_history_html = f"""<div style="margin-top: 1rem;"><div style="font-size: 0.9rem; font-weight: 600; color: #5f6368; margin-bottom: 0.5rem; display:flex; align-items:center;">SOURCES</div><div style="overflow-x: auto; white-space: nowrap; padding-bottom: 10px;">{sources_html_accum}</div></div><div style="margin-top: 1rem; font-size: 1.05rem; line-height: 1.7; color: #1f1f1f;"><span style="font-size: 1.2rem; margin-right: 5px;">✨</span> <strong>Answer</strong><br>{full_response_text}</div>"""
            
            current_messages.append({
                "role": "assistant", 
                "content": final_history_html,
                "plain_text": full_response_text
            })
            st.session_state.last_search_time = time.time()
            st.rerun() # Rerun to solidify the state and remove the "Thinking" UI from the loop
            
        else:
            st.warning("No results found.")
    except Exception as e:
        # Robust error handling for Quota Exceeded with Exponential Backoff
        error_str = str(e)
        if "429" in error_str or "Quota exceeded" in error_str:
            st.warning("⚠️ Quota exceeded. Attempting auto-retry (up to 3 times)...")
            
            retry_count = 0
            max_retries = 3
            success = False
            
            while retry_count < max_retries and not success:
                wait_time = (retry_count + 1) * 10 # 10s, 20s, 30s
                with st.spinner(f"Waiting {wait_time}s to cooldown..."):
                    time.sleep(wait_time)
                
                try:
                    stream = generate_answer(last_user_query, results, current_messages[:-1])
                    full_response_text = ""
                    for chunk in stream:
                        full_response_text += chunk.text
                        answer_placeholder.markdown(full_response_text)
                    
                    final_history_html = f"""<div style="margin-top: 1rem;"><div style="font-size: 0.9rem; font-weight: 600; color: #5f6368; margin-bottom: 0.5rem; display:flex; align-items:center;">SOURCES</div><div style="overflow-x: auto; white-space: nowrap; padding-bottom: 10px;">{sources_html_accum}</div></div><div style="margin-top: 1rem; font-size: 1.05rem; line-height: 1.7; color: #1f1f1f;"><span style="font-size: 1.2rem; margin-right: 5px;">✨</span> <strong>Answer</strong><br>{full_response_text}</div>"""
                    
                    current_messages.append({
                        "role": "assistant", 
                        "content": final_history_html,
                        "plain_text": full_response_text
                    })
                    st.session_state.last_search_time = time.time()
                    st.rerun()
                    success = True
                except Exception as retry_e:
                    retry_count += 1
                    if retry_count == max_retries:
                         st.error(f"Failed after retries. Please wait a minute before asking again. (API Quota)")
        else:
            st.error(f"An error occurred: {e}")
