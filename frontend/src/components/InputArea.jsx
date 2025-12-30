import React, { useState, useEffect } from 'react';
import { ArrowUp, Mic, MicOff } from 'lucide-react';

const InputArea = ({ onSend, disabled }) => {
    const [input, setInput] = useState('');
    const [isListening, setIsListening] = useState(false);
    const [recognition, setRecognition] = useState(null);

    useEffect(() => {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const recognizer = new SpeechRecognition();
            recognizer.continuous = false;
            recognizer.interimResults = false;
            recognizer.lang = 'en-US';

            recognizer.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                setInput((prev) => prev + (prev ? ' ' : '') + transcript);
                setIsListening(false);
            };

            recognizer.onerror = (event) => {
                console.error("Speech recognition error", event.error);
                setIsListening(false);
            };

            recognizer.onend = () => {
                setIsListening(false);
            };

            setRecognition(recognizer);
        }
    }, []);

    const toggleListening = () => {
        if (!recognition) {
            alert("Your browser does not support voice input.");
            return;
        }

        if (isListening) {
            recognition.stop();
        } else {
            recognition.start();
            setIsListening(true);
        }
    };

    const handleSend = () => {
        if (!input.trim() || disabled) return;
        onSend(input);
        setInput('');
    };

    return (
        <div className="w-full max-w-3xl mx-auto pb-6 px-4">
            <form
                onSubmit={(e) => { e.preventDefault(); handleSend(); }}
                className="relative flex items-center bg-[#f0f4f9] rounded-full p-2 border border-transparent focus-within:border-gray-200 focus-within:bg-white focus-within:shadow-md transition-all"
            >
                <button
                    type="button"
                    onClick={toggleListening}
                    className={`p-2 rounded-full transition-colors mr-2 ${isListening ? 'bg-red-100 text-red-600 animate-pulse' : 'text-gray-500 hover:bg-gray-200'}`}
                    title="Voice Input"
                >
                    {isListening ? <MicOff size={20} /> : <Mic size={20} />}
                </button>

                <input
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder={isListening ? "Listening..." : "Message Exponentia AI..."}
                    className="flex-1 bg-transparent border-none outline-none px-2 py-3 text-gray-700 placeholder-gray-500 text-base min-w-0"
                    disabled={disabled}
                />
                <button
                    type="submit"
                    disabled={!input.trim() || disabled}
                    className="bg-[#e0e4e9] hover:bg-[#d0d6dd] text-gray-600 p-2 rounded-full transition-colors disabled:opacity-50 disabled:cursor-not-allowed mx-1 flex-shrink-0"
                >
                    <ArrowUp size={20} />
                </button>
            </form>
        </div>
    );
};

export default InputArea;
