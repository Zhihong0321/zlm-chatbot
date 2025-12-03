import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { PaperAirplaneIcon, PlusIcon, ChatBubbleLeftRightIcon, ExclamationCircleIcon, ArrowLeftIcon } from '@heroicons/react/24/outline';

// Cookie helper functions
const setUserCookie = (agentId: string, sessionId: string) => {
  const cookieName = `chat_session_${agentId}`;
  document.cookie = `${cookieName}=${sessionId}; max-age=30*24*60*60; path=/`; // 30 days
};

const getUserCookie = (agentId: string): string | null => {
  const cookieName = `chat_session_${agentId}`;
  const cookies = document.cookie.split(';');
  for (const cookie of cookies) {
    const [name, value] = cookie.trim().split('=');
    if (name === cookieName) return value;
  }
  return null;
};

export default function MobileTesterChat() {
  const { agentId, sessionId } = useParams();
  const navigate = useNavigate();
  
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [agent, setAgent] = useState<any>(null);
  const [agentLoading, setAgentLoading] = useState(true);
  const [error, setError] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load agent
  useEffect(() => {
    if (!agentId) return;
    
    api.getAgent(agentId)
      .then(res => {
        setAgent(res.data);
        setAgentLoading(false);
      })
      .catch(err => {
        setError('Agent not found');
        setAgentLoading(false);
      });
  }, [agentId]);

  // Check existing session or create new one
  useEffect(() => {
    if (!agent) return;
    
    const currentSessionId = sessionId || getUserCookie(agentId);
    
    if (currentSessionId) {
      // Use existing session
      if (currentSessionId !== sessionId) {
        // Navigate to the session if we're not already there
        navigate(`/tester/${agentId}/chat/${currentSessionId}`, { replace: true });
      } else {
        // Load messages for current session
        loadMessages();
      }
    } else {
      // Create new session for new users
      createNewSession();
    }
  }, [agent]);

  // Load messages when sessionId exists
  useEffect(() => {
    if (!sessionId || !agent) return;
    
    loadMessages();
  }, [sessionId, agent]);

  // Scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const createNewSession = async () => {
    try {
      const res = await api.createSession({
        title: 'New Chat',
        agent_id: agent.id
      });
      const newSessionId = res.data.id;
      setUserCookie(agentId!, newSessionId);
      navigate(`/tester/${agentId}/chat/${newSessionId}`);
    } catch (err) {
      setError('Failed to create session');
    }
  };

  const handleViewSessions = () => {
    navigate(`/tester/${agentId}/sessions`);
  };

  const loadMessages = async () => {
    if (!sessionId) return;
    
    try {
      const res = await api.getSessionHistory(sessionId);
      setMessages(res.data);
    } catch (err) {
      console.error('Failed to load messages:', err);
    }
  };

  const handleSend = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!input.trim() || !sessionId || loading) return;

    const messageText = input.trim();
    const tempUserMessage = {
      id: 'temp-user-' + Date.now(),
      role: 'user',
      content: messageText,
      created_at: new Date().toISOString()
    };

    // Add user message immediately to UI
    setMessages(prev => [...prev, tempUserMessage]);
    setInput('');
    setLoading(true);
    setError('');

    try {
      // Send to backend and get response
      const res = await api.sendMessage(sessionId, { message: messageText });
      
      // Remove temp message and add real messages
      setMessages(prev => [...prev.filter(m => m.id !== tempUserMessage.id), res.data]);
      
      // Ensure we have both user and AI messages by reloading
      await loadMessages();
    } catch (err) {
      console.error('Send failed:', err);
      setError('Failed to send message');
      // Remove temp message on error
      setMessages(prev => prev.filter(m => m.id !== tempUserMessage.id));
      setInput(messageText);
    } finally {
      setLoading(false);
    }
  };

  // Helper to safely format date
  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    } catch {
      return 'Invalid time';
    }
  };

  if (agentLoading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <div className="text-gray-500">Loading agent...</div>
      </div>
    );
  }

  if (error || !agent) {
    return (
      <div className="flex flex-col items-center justify-center h-screen bg-gray-50 p-4 text-center">
        <ExclamationCircleIcon className="w-12 h-12 text-red-500 mb-2" />
        <h2 className="text-xl font-bold text-gray-800">Agent Not Found</h2>
        <p className="text-gray-600">The agent link might be invalid or expired.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen bg-white max-h-screen">
      {/* Header */}
      <header className="flex items-center justify-between px-4 py-3 bg-white border-b border-gray-200 shrink-0">
        <div className="flex items-center gap-3 overflow-hidden">
            <button
              onClick={handleViewSessions}
              className="p-2 rounded-full text-gray-600 hover:bg-gray-100"
            >
              <ArrowLeftIcon className="w-5 h-5" />
            </button>
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold shrink-0">
                {agent.name.charAt(0)}
            </div>
            <div className="min-w-0">
                <h1 className="font-bold text-gray-900 truncate leading-tight">{agent.name}</h1>
                <p className="text-xs text-gray-500 truncate">Chat</p>
            </div>
        </div>
        <div className="flex items-center gap-2">
            <button
                onClick={createNewSession}
                className="p-2 rounded-full bg-gray-100 text-gray-600 hover:bg-gray-200 transition-colors"
                title="New Chat"
            >
                <PlusIcon className="w-5 h-5" />
            </button>
        </div>
      </header>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 min-h-0">
        {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center min-h-full text-gray-400 space-y-4 py-8">
                <ChatBubbleLeftRightIcon className="w-16 h-16" />
                <p className="text-lg">Start chatting with {agent.name}</p>
            </div>
        )}
        
        {messages.map((msg) => (
          <div key={msg.id} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
            <div
              className={`max-w-[85%] p-3 rounded-2xl text-sm shadow-sm ${
                msg.role === 'user'
                  ? 'bg-blue-600 text-white rounded-br-none'
                  : 'bg-white text-gray-800 border border-gray-200 rounded-bl-none'
              }`}
            >
              <div className="whitespace-pre-wrap break-words">{msg.content}</div>
            </div>
            
            {/* Reasoning Content for Assistant Messages */}
            {msg.role === 'assistant' && msg.reasoning_content && (
              <div className="mt-2 max-w-[85%] p-3 rounded-xl bg-purple-50 border border-purple-100 text-xs text-purple-800">
                <div className="flex items-center gap-1.5 mb-1 font-semibold text-purple-700 uppercase tracking-wider text-[10px]">
                  Reasoning Process
                </div>
                <div className="whitespace-pre-wrap leading-relaxed opacity-90 break-words">
                  {msg.reasoning_content}
                </div>
              </div>
            )}
            
            <span className="text-[10px] text-gray-400 mt-1 px-1">
                {formatDate(msg.created_at)}
            </span>
          </div>
        ))}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="shrink-0 p-3 bg-white border-t border-gray-200">
        {loading && (
            <div className="mb-2 text-center">
                 <div className="inline-flex items-center gap-2 bg-blue-50 border border-blue-200 px-3 py-2 rounded-full shadow-sm">
                    <div className="flex space-x-1">
                        <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                        <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                        <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                    </div>
                    <div className="text-xs text-blue-600 font-medium">Agent is thinking...</div>
                 </div>
            </div>
        )}
        <form
            onSubmit={handleSend}
            className="flex items-center gap-2 bg-white border border-gray-300 rounded-full px-4 py-3 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-500 focus-within:ring-opacity-20 transition-all shadow-sm"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type a message..."
            className="flex-1 bg-transparent border-none focus:ring-0 text-base h-5 placeholder-gray-500 text-gray-900"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="p-2 rounded-full bg-blue-600 text-white disabled:opacity-50 hover:bg-blue-700 transition-all flex-shrink-0"
          >
            <PaperAirplaneIcon className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
}
