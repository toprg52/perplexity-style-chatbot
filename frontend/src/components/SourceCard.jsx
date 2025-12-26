import React from 'react';

const SourceCard = ({ sources }) => {
    if (!sources || sources.length === 0) return null;

    return (
        <div className="mb-6">
            <div className="flex items-center gap-2 mb-3 text-sm font-semibold text-gray-600 uppercase tracking-wide">
                <span>🔗</span> Sources
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {sources.map((source, idx) => {
                    const domain = source.url.split('/')[2].replace('www.', '');
                    return (
                        <a
                            key={idx}
                            href={source.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="bg-[#f0f4f9] p-3 rounded-2xl hover:bg-[#e2e7eb] transition-colors flex flex-col justify-between h-[80px]"
                        >
                            <div className="text-xs font-semibold text-gray-800 line-clamp-2 leading-tight">
                                {source.title}
                            </div>
                            <div className="flex items-center gap-1 text-[10px] text-gray-500">
                                <img
                                    src={`https://www.google.com/s2/favicons?domain=${source.url}`}
                                    alt=""
                                    className="w-3 h-3 opacity-70"
                                />
                                <span className="truncate">{domain}</span>
                            </div>
                        </a>
                    );
                })}
            </div>
        </div>
    );
};

export default SourceCard;
