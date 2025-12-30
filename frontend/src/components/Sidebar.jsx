import React, { useState, useRef, useEffect } from 'react';
import { Plus, MoreHorizontal, Pencil, Trash2, X, Check } from 'lucide-react';

const Sidebar = ({ sessions, currentSessionId, onSelectSession, onNewChat, onRenameSession, onDeleteSession, isOpen, onClose }) => {
    const [menuOpenId, setMenuOpenId] = useState(null);
    const [renamingId, setRenamingId] = useState(null);
    const [renameValue, setRenameValue] = useState("");
    const menuRef = useRef(null);

    // Close menu when clicking outside
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (menuRef.current && !menuRef.current.contains(event.target)) {
                setMenuOpenId(null);
            }
        };
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    const handleMenuClick = (e, id) => {
        e.stopPropagation();
        if (menuOpenId === id) {
            setMenuOpenId(null);
        } else {
            setMenuOpenId(id);
        }
    };

    const handleRenameStart = (e, session) => {
        e.stopPropagation();
        setRenamingId(session.id);
        setRenameValue(session.title);
        setMenuOpenId(null);
    };

    const handleRenameSubmit = (e, id) => {
        e.stopPropagation();
        if (renameValue.trim()) {
            onRenameSession(id, renameValue.trim());
        }
        setRenamingId(null);
    };

    const handleRenameCancel = (e) => {
        e.stopPropagation();
        setRenamingId(null);
    };

    const handleDeleteClick = (e, id) => {
        e.stopPropagation();
        if (confirm("Are you sure you want to delete this chat?")) {
            onDeleteSession(id);
        }
        setMenuOpenId(null);
    };

    return (
        <>
            {/* Mobile Overlay */}
            {isOpen && (
                <div
                    className="fixed inset-0 bg-black/50 z-40 md:hidden"
                    onClick={onClose}
                />
            )}

            {/* Sidebar Container */}
            <div className={`
                fixed inset-y-0 left-0 z-50 w-[300px] bg-[#f0f4f9] border-r border-gray-200 flex flex-col p-4 transition-transform duration-300 transform
                ${isOpen ? "translate-x-0" : "-translate-x-full"}
                md:relative md:translate-x-0 md:flex
            `}>
                <div className="mb-6">
                    <div className="flex items-center justify-between mb-6">
                        <span className="text-xl font-bold text-gray-700">exponentia<span className="text-[#4285F4]">.ai</span></span>
                        <button onClick={onClose} className="md:hidden p-1 text-gray-500 hover:text-gray-700">
                            <X size={24} />
                        </button>
                    </div>

                    <button
                        onClick={onNewChat}
                        className="w-full flex items-center justify-center gap-2 bg-[#dde3ea] hover:bg-[#cdd5df] text-gray-700 py-3 rounded-full font-medium transition-colors"
                    >
                        <Plus size={20} />
                        New Chat
                    </button>
                </div>

                <div className="flex-1 overflow-y-auto">
                    <div className="text-xs font-semibold text-gray-500 mb-2 uppercase tracking-wide px-2">My Chats</div>
                    <div className="space-y-1">
                        {sessions.map((session) => (
                            <div key={session.id} className="relative group">
                                {renamingId === session.id ? (
                                    <div className="flex items-center gap-1 px-4 py-2 bg-white rounded-full border border-blue-400">
                                        <input
                                            autoFocus
                                            value={renameValue}
                                            onChange={(e) => setRenameValue(e.target.value)}
                                            onClick={(e) => e.stopPropagation()}
                                            onKeyDown={(e) => {
                                                if (e.key === 'Enter') handleRenameSubmit(e, session.id);
                                                if (e.key === 'Escape') handleRenameCancel(e);
                                            }}
                                            className="flex-1 bg-transparent outline-none text-sm min-w-0"
                                        />
                                        <button onClick={(e) => handleRenameSubmit(e, session.id)} className="text-green-600 hover:text-green-700"><Check size={14} /></button>
                                        <button onClick={(e) => handleRenameCancel(e)} className="text-red-500 hover:text-red-700"><X size={14} /></button>
                                    </div>
                                ) : (
                                    <button
                                        onClick={() => onSelectSession(session.id)}
                                        className={`w-full text-left px-4 py-2 rounded-full text-sm font-medium truncate transition-all pr-10 relative ${currentSessionId === session.id
                                            ? 'bg-[#d3e3fd] text-[#001d35]'
                                            : 'text-gray-700 hover:bg-[#e2e7eb]'
                                            }`}
                                    >
                                        <span className="truncate block">{session.title || "New Chat"}</span>

                                        {/* Three dots - visible on hover or if menu is open - Mobile always visible? No, stick to hover/active */}
                                        <div
                                            onClick={(e) => handleMenuClick(e, session.id)}
                                            className={`absolute right-2 top-1/2 -translate-y-1/2 p-1 rounded-full hover:bg-black/10 transition-opacity ${menuOpenId === session.id ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'}`}
                                        >
                                            <MoreHorizontal size={16} />
                                        </div>
                                    </button>
                                )}

                                {/* Dropdown Menu */}
                                {menuOpenId === session.id && (
                                    <div ref={menuRef} className="absolute right-0 top-full mt-1 w-32 bg-white rounded-lg shadow-lg border border-gray-100 z-20 overflow-hidden">
                                        <button
                                            onClick={(e) => handleRenameStart(e, session)}
                                            className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2"
                                        >
                                            <Pencil size={14} /> Rename
                                        </button>
                                        <button
                                            onClick={(e) => handleDeleteClick(e, session.id)}
                                            className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center gap-2"
                                        >
                                            <Trash2 size={14} /> Delete
                                        </button>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                </div>

                <div className="mt-4 text-xs text-center text-gray-400">
                    Powered by Gemini 2.0 & Tavily
                </div>
            </div>
        </>
    );
};

export default Sidebar;
