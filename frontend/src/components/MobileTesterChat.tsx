import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { api } from '../services/api';
import { PaperAirplaneIcon, PlusIcon, ChatBubbleLeftRightIcon, ExclamationCircleIcon } from '@heroicons/react/24/outline';

export default function MobileTesterChat() {
  const { agentId } = useParams();
  
  const [sessionId, setSessionId] = useState<string | null>(null);
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

  // Create session when agent loads
  useEffect(() => {
    if (agent && !sessionId) {
      createNewSession();
    }
  }, [agent]);

  // Load messages when sessionId changes
  useEffect(() => {
    if (!sessionId) return;
    
    loadMessages();
  }, [sessionId]);

  // Scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const createNewSession = async () => {
    try {
      const res = await api.createSession({
        title: `Tester Chat - ${new Date().toLocaleTimeString()}`,
        agent_id: agent.id
      });
      setSessionId(res.data.id);
    } catch (err) {
      setError('Failed to create session');
    }
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
    setInput('');
    setLoading(true);
    setError('');

    try {
      // Send to backend and get response
      const res = await api.sendMessage(sessionId, { message: messageText });
      
      // Reload messages (both user and AI will be in DB)
      await loadMessages();
    } catch (err) {
      console.error('Send failed:', err);
      setError('Failed to send message');
      // Restore input on error
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
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold shrink-0">
                {agent.name.charAt(0)}
            </div>
            <div className="min-w-0">
                <h1 className="font-bold text-gray-900 truncate leading-tight">{agent.name}</h1>
                <p className="text-xs text-gray-500 truncate">Tester View</p>
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
        
        {loading && (
            <div className="flex flex-col items-start mb-4">
                 <div className="flex items-center gap-2 max-w-[85%] bg-blue-50 border border-blue-200 p-4 rounded-2xl rounded-bl-none shadow-sm">
                    <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                    </div>
                    <div className="text-xs text-blue-600 font-medium">Agent is thinking...</div>
                 </div>
            </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="shrink-0 p-3 bg-white border-t border-gray-200">
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
