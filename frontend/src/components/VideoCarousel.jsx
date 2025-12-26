import React from 'react';

const VideoCarousel = ({ videos }) => {
    if (!videos || videos.length === 0) return null;

    const extractThumbnail = (url) => {
        // Basic extraction, reliable for standard links
        const match = url.match(/(?:youtu\.be\/|youtube\.com\/watch\?v=)([\w-]+)/);
        const id = match ? match[1] : null;
        return id ? `https://img.youtube.com/vi/${id}/mqdefault.jpg` : null;
    };

    return (
        <div className="mb-6">
            <div className="flex items-center gap-2 mb-3 text-sm font-semibold text-gray-600 uppercase tracking-wide">
                <span>📺</span> Videos
            </div>
            <div className="flex overflow-x-auto gap-4 pb-4 scrollbar-thin">
                {videos.map((video, idx) => {
                    const thumb = extractThumbnail(video.url);
                    if (!thumb) return null;
                    return (
                        <a
                            key={idx}
                            href={video.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex-none w-[240px] group bg-[#f0f4f9] rounded-xl overflow-hidden hover:translate-y-[-2px] transition-transform"
                        >
                            <img src={thumb} className="w-full h-[135px] object-cover" alt={video.title} />
                            <div className="p-3">
                                <div className="text-sm font-semibold text-gray-800 line-clamp-2 leading-tight mb-1">
                                    {video.title}
                                </div>
                                <div className="text-xs text-gray-500">YouTube</div>
                            </div>
                        </a>
                    );
                })}
            </div>
        </div>
    );
};

export default VideoCarousel;
