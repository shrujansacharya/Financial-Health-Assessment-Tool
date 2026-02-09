import { useState, useRef, useEffect } from 'react';
import { X, Send, Bot } from 'lucide-react';

interface Message {
    id: string;
    text: string;
    sender: 'user' | 'bot';
    timestamp: Date;
}

export default function ChatInterface() {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState<Message[]>([
        {
            id: '1',
            text: "Hi! I'm your AI Financial Analyst. Ask me anything about your uploaded data. e.g., 'Why did my score drop?' or 'What is my highest expense?'",
            sender: 'bot',
            timestamp: new Date()
        }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isOpen]);

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMsg: Message = {
            id: Date.now().toString(),
            text: input,
            sender: 'user',
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setLoading(true);

        try {
            const response = await fetch('http://localhost:8000/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: userMsg.text })
            });

            const data = await response.json();

            const botMsg: Message = {
                id: (Date.now() + 1).toString(),
                text: data.answer || "Sorry, I couldn't analyze that.",
                sender: 'bot',
                timestamp: new Date()
            };

            setMessages(prev => [...prev, botMsg]);
        } catch (error) {
            console.error(error);
            const errorMsg: Message = {
                id: (Date.now() + 1).toString(),
                text: "Error connecting to the AI Analyst. Please ensure the backend is running.",
                sender: 'bot',
                timestamp: new Date()
            };
            setMessages(prev => [...prev, errorMsg]);
        } finally {
            setLoading(false);
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter') handleSend();
    };

    return (
        <div className="fixed bottom-6 right-6 z-[100] flex flex-col items-end font-sans">
            {/* Chat Panel */}
            {isOpen && (
                <div className="w-[400px] h-[85vh] max-h-[800px] flex flex-col bg-[#0b0f19]/90 backdrop-blur-xl border border-white/10 rounded-3xl shadow-2xl overflow-hidden animate-in slide-in-from-bottom-5 fade-in duration-300">

                    {/* Header */}
                    <div className="flex items-center justify-between px-6 py-4 border-b border-white/5 bg-white/5 backdrop-blur-md">
                        <div className="flex items-center gap-3">
                            <div className="relative">
                                <div className="w-2.5 h-2.5 bg-emerald-500 rounded-full animate-pulse shadow-[0_0_10px_rgba(16,185,129,0.5)]"></div>
                            </div>
                            <div>
                                <h3 className="text-sm font-semibold text-white tracking-wide">AI Analyst</h3>
                                <p className="text-[10px] text-gray-400 font-medium tracking-wider uppercase">Financial Copilot</p>
                            </div>
                        </div>
                        <button
                            onClick={() => setIsOpen(false)}
                            className="p-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-full transition-all"
                        >
                            <X size={18} />
                        </button>
                    </div>

                    {/* Messages Area */}
                    <div className="flex-1 overflow-y-auto p-5 space-y-5 custom-scrollbar scroll-smooth">
                        {/* Intro Context Card */}
                        {messages.length < 2 && (
                            <div className="p-4 rounded-xl bg-indigo-500/10 border border-indigo-500/20 mb-4">
                                <p className="text-xs text-indigo-200 leading-relaxed">
                                    <span className="font-semibold block mb-1 text-indigo-100">👋 Hi there!</span>
                                    I'm your dedicated Financial Analyst. I've studied your uploaded data and can answer questions about revenue, risks, and growth anytime.
                                </p>
                            </div>
                        )}

                        {messages.map((msg) => (
                            <div
                                key={msg.id}
                                className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                            >
                                <div
                                    className={`max-w-[85%] px-4 py-3 text-sm leading-relaxed shadow-sm ${msg.sender === 'user'
                                        ? 'bg-indigo-600 text-white rounded-2xl rounded-tr-sm'
                                        : 'bg-white/5 text-gray-200 border border-white/5 rounded-2xl rounded-tl-sm'
                                        }`}
                                >
                                    {msg.text}
                                </div>
                            </div>
                        ))}

                        {/* Loading Indicator */}
                        {loading && (
                            <div className="flex justify-start">
                                <div className="bg-white/5 px-4 py-3 rounded-2xl rounded-tl-sm border border-white/5 flex gap-1.5 items-center">
                                    <span className="text-xs text-gray-400 mr-2">Analyzing...</span>
                                    <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                                    <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                                    <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input Area */}
                    <div className="p-4 bg-[#0b0f19] border-t border-white/5">
                        <div className="relative flex items-center">
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={handleKeyPress}
                                placeholder="Ask about your finances..."
                                className="w-full bg-white/5 border border-white/10 rounded-full pl-5 pr-12 py-3 text-sm text-white placeholder:text-gray-500 focus:outline-none focus:border-indigo-500/50 focus:bg-white/10 transition-all font-medium"
                            />
                            <button
                                onClick={handleSend}
                                disabled={loading || !input.trim()}
                                className="absolute right-1.5 p-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-full disabled:opacity-50 disabled:bg-gray-700 transition-all shadow-lg hover:shadow-indigo-500/25"
                            >
                                <Send size={16} className={loading ? "opacity-0" : "opacity-100"} />
                            </button>
                        </div>
                        <p className="text-[10px] text-center text-gray-600 mt-2">
                            AI insights are indicative. Not financial advice.
                        </p>
                    </div>
                </div>
            )}

            {/* Floating Toggle Button (Premium Pill Style) */}
            {!isOpen && (
                <button
                    onClick={() => setIsOpen(true)}
                    className="group flex items-center gap-3 px-5 py-3 bg-[#0b0f19] border border-indigo-500/30 hover:border-indigo-500/60 text-white rounded-full shadow-[0_8px_30px_rgb(0,0,0,0.3)] hover:shadow-indigo-500/10 transition-all duration-300 hover:-translate-y-1"
                >
                    <div className="relative">
                        <Bot size={20} className="text-indigo-400" />
                        <span className="absolute -top-0.5 -right-0.5 flex h-2.5 w-2.5">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
                        </span>
                    </div>
                    <span className="text-sm font-medium text-gray-200 group-hover:text-white">Ask AI Analyst</span>
                </button>
            )}
        </div>
    );
}
