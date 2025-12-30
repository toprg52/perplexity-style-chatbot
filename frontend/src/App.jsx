import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';
import api, { createSession, getSessions, getSessionHistory, updateSessionTitle, deleteSession, API_URL } from './api/client';

const App = () => {
  const [sessions, setSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);

  // Load sessions on mount
  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      const data = await getSessions();
      setSessions(data);
      // Automatically select first session (most recent) if available
      if (data.length > 0 && !currentSessionId) {
        loadHistory(data[0].id);
      }
    } catch (error) {
      console.error("Failed to load sessions", error);
    }
  };

  const loadHistory = async (id) => {
    try {
      const session = await getSessionHistory(id);
      setCurrentSessionId(id);
      setMessages(session.messages || []);
    } catch (error) {
      console.error("Failed to load history", error);
    }
  };

  const handleNewChat = async () => {
    // Don't create on backend until first message? Or create immediately?
    // User style: Create immediately on button click
    try {
      const session = await createSession();
      setSessions([session, ...sessions]);
      setCurrentSessionId(session.id);
      setMessages([]);
    } catch (e) {
      console.error(e);
    }
  };

  const handleSendMessage = async (text) => {
    let activeSessionId = currentSessionId;

    if (!activeSessionId) {
      // Create session first if not exists
      try {
        const session = await createSession();
        setSessions([session, ...sessions]);
        activeSessionId = session.id;
        setCurrentSessionId(activeSessionId);
      } catch (e) {
        console.error(e);
        alert("Failed to connect to the backend. Please ensure the backend server and MongoDB are running.");
        return;
      }
    }

    // Add user message optimistically
    const userMsg = { role: 'user', content: text };
    setMessages(prev => [...prev, userMsg]);
    setIsStreaming(true);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: activeSessionId, message: text })
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let assistantMsg = { role: 'assistant', content: '', sources: [] };

      // Add placeholder assistant message
      setMessages(prev => [...prev, assistantMsg]);

      let isFirstChunk = true;
      let buffer = "";
      let hasParsedSources = false;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });

        let contentToAdd = "";

        if (!hasParsedSources) {
          buffer += chunk;
          // Check if buffer contains the split token
          if (buffer.includes('\n--split--\n')) {
            const parts = buffer.split('\n--split--\n');
            // parts[0] is sources JSON, parts[1] is start of text (if any)
            try {
              const sourceData = JSON.parse(parts[0]);
              assistantMsg.sources = sourceData.data;
            } catch (e) {
              console.error("Error parsing sources", e);
            }
            contentToAdd = parts.slice(1).join('\n--split--\n'); // Rejoin rest if multiple splits (unlikely) or just take part 1
            hasParsedSources = true;
            buffer = ""; // Clear buffer
          } else {
            // Continue buffering, don't display anything yet to avoid showing raw JSON
            continue;
          }
        } else {
          // Sources already parsed, this is just text content
          contentToAdd = chunk;
        }

        assistantMsg.content += contentToAdd;

        // Update state
        setMessages(prev => {
          const newMsgs = [...prev];
          newMsgs[newMsgs.length - 1] = { ...assistantMsg };
          return newMsgs;
        });
      }

      // Refresh sessions list to update title if changed
      loadSessions();

    } catch (error) {
      console.error("Chat error", error);
      setMessages(prev => [...prev, { role: 'assistant', content: "Error: Could not connect to backend." }]);
    } finally {
      setIsStreaming(false);
    }
  };

  const handleRenameSession = async (id, newTitle) => {
    try {
      await updateSessionTitle(id, newTitle);
      setSessions(sessions.map(s => s.id === id ? { ...s, title: newTitle } : s));
    } catch (e) {
      console.error("Failed to rename session", e);
    }
  };

  const handleDeleteSession = async (id) => {
    try {
      await deleteSession(id);
      setSessions(sessions.filter(s => s.id !== id));
      if (currentSessionId === id) {
        setCurrentSessionId(null);
        setMessages([]);
      }
    } catch (e) {
      console.error("Failed to delete session", e);
    }
  };

  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  return (
    <div className="flex bg-white h-screen overflow-hidden relative">
      <Sidebar
        sessions={sessions}
        currentSessionId={currentSessionId}
        onSelectSession={(id) => {
          loadHistory(id);
          setIsSidebarOpen(false); // Close sidebar on selection on mobile
        }}
        onNewChat={() => {
          handleNewChat();
          setIsSidebarOpen(false);
        }}
        onRenameSession={handleRenameSession}
        onDeleteSession={handleDeleteSession}
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
      />
      <ChatArea
        messages={messages}
        isStreaming={isStreaming}
        onSendMessage={handleSendMessage}
        isNewChat={!messages.length}
        onOpenSidebar={() => setIsSidebarOpen(true)}
      />
    </div>
  );
};

export default App;
