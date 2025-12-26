import React, { useRef, useEffect } from 'react';
import MessageBubble from './MessageBubble';
import InputArea from './InputArea';

const ChatArea = ({ messages, isStreaming, onSendMessage, isNewChat }) => {
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isStreaming]);

    // Landing Page View
    if (isNewChat && messages.length === 0) {
        const suggestions = [
            "Create a workout plan",
            "Python script for SEO",
            "Explain Quantum Physics",
            "Trends in AI Agents"
        ];

        return (
            <div className="flex-1 flex flex-col h-screen relative">
                <div className="flex-1 flex flex-col items-center justify-center p-4">
                    <h1 className="text-5xl font-medium mb-4 bg-gradient-to-r from-[#4285F4] via-[#9B72CB] to-[#D96570] text-transparent bg-clip-text text-center">
                        Hello, Human
                    </h1>
                    <p className="text-2xl text-gray-400 font-light mb-12">How can I help you today?</p>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 w-full max-w-4xl mb-8">
                        {suggestions.map((s, i) => (
                            <button
                                key={i}
                                onClick={() => onSendMessage(s)}
                                className="p-4 bg-[#f0f4f9] rounded-2xl text-left hover:bg-[#dde3ea] transition-colors text-gray-800 font-medium"
                            >
                                {s}
                            </button>
                        ))}
                    </div>
                </div>

                <div className="w-full bg-gradient-to-t from-white via-white to-transparent pt-10">
                    <InputArea onSend={onSendMessage} disabled={isStreaming} />
                </div>
            </div>
        );
    }

    return (
        <div className="flex-1 flex flex-col h-screen relative bg-white">
            {/* Sticky Header - Top Branding */}
            <div className="sticky top-0 z-10 bg-white/80 backdrop-blur-md border-b border-gray-100 py-3 flex justify-center">
                <div className="text-xl font-bold text-gray-700">exponentia<span className="text-[#4285F4]">.ai</span></div>
            </div>

            <div className="flex-1 overflow-y-auto px-4 py-6 scrollbar-thin">
                <div className="max-w-3xl mx-auto">
                    {messages.map((msg, index) => (
                        <MessageBubble key={index} message={msg} />
                    ))}
                    {isStreaming && (
                        <div className="flex items-center gap-2 text-gray-400 ml-4 mb-4 animate-pulse">
                            <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
                            <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
                            <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>
            </div>

            <div className="w-full bg-gradient-to-t from-white via-white to-transparent pt-4">
                <InputArea onSend={onSendMessage} disabled={isStreaming} />
            </div>
        </div>
    );
};

export default ChatArea;
