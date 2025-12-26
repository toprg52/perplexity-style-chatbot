import React from 'react';
import ReactMarkdown from 'react-markdown';
import SourceCard from './SourceCard';
import VideoCarousel from './VideoCarousel';

const MessageBubble = ({ message }) => {
    const isUser = message.role === 'user';

    // Parse sources from message if available (usually attached to assistant message)
    const sources = message.sources || [];
    const videoResults = sources.filter(s => s.url.includes('youtube.com') || s.url.includes('youtu.be'));
    const webResults = sources.filter(s => !s.url.includes('youtube.com') && !s.url.includes('youtu.be'));

    return (
        <div className={`flex w-full mb-6 ${isUser ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] md:max-w-[75%] ${isUser ? 'bg-[#f0f4f9] rounded-[24px_24px_4px_24px] px-6 py-4' : 'w-full'}`}>
                {isUser ? (
                    <div className="text-[#1f1f1f] text-base">{message.content}</div>
                ) : (
                    <div>
                        {/* Sources & Videos (Only show if we have them) */}
                        {(videoResults.length > 0) && <VideoCarousel videos={videoResults} />}
                        {(webResults.length > 0) && <SourceCard sources={webResults} />}

                        <div className="flex items-center gap-2 mb-2 text-sm font-semibold text-gray-600 uppercase tracking-wide mt-6">
                            <span>✨</span> Answer
                        </div>
                        <div className="prose prose-slate max-w-none text-[#1f1f1f] leading-7">
                            <ReactMarkdown
                                components={{
                                    a: ({ node, ...props }) => <a {...props} className="text-blue-600 hover:underline" target="_blank" rel="noopener noreferrer" />
                                }}
                            >
                                {message.content}
                            </ReactMarkdown>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default MessageBubble;
