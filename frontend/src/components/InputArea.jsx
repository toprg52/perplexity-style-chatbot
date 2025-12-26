import React, { useState } from 'react';
import { ArrowUp } from 'lucide-react';

const InputArea = ({ onSend, disabled }) => {
    const [input, setInput] = useState('');

    const handleSend = () => {
        if (!input.trim() || disabled) return;
        onSend(input);
        setInput('');
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div className="w-full max-w-3xl mx-auto pb-6 px-4">
            <div className="relative flex items-center bg-[#f0f4f9] rounded-full p-2 border border-transparent focus-within:border-gray-200 focus-within:bg-white focus-within:shadow-md transition-all">
                <input
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Message Exponentia AI..."
                    className="flex-1 bg-transparent border-none outline-none px-4 py-3 text-gray-700 placeholder-gray-500 text-base"
                    disabled={disabled}
                />
                <button
                    onClick={handleSend}
                    disabled={!input.trim() || disabled}
                    className="bg-[#e0e4e9] hover:bg-[#d0d6dd] text-gray-600 p-2 rounded-full transition-colors disabled:opacity-50 disabled:cursor-not-allowed mx-1"
                >
                    <ArrowUp size={20} />
                </button>
            </div>
        </div>
    );
};

export default InputArea;
