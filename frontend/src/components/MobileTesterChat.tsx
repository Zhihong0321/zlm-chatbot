import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';
import { PaperAirplaneIcon, PlusIcon, ArrowPathIcon, EyeIcon, EyeSlashIcon, ChatBubbleLeftRightIcon, ExclamationCircleIcon } from '@heroicons/react/24/outline';

export default function MobileTesterChat() {
  const { agentId } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [input, setInput] = useState('');
  const [showReasoning, setShowReasoning] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [isAutoScrolling, setIsAutoScrolling] = useState(true);

  // Fetch Agent Details
  const { data: agent, isLoading: agentLoading, error: agentError } = useQuery({
    queryKey: ['agent', agentId],
    queryFn: () => api.getAgent(agentId || '').then(res => res.data),
    enabled: !!agentId
  });

  // Fetch Messages if session exists
  const { data: messages = [], isLoading: messagesLoading } = useQuery({
    queryKey: ['messages', sessionId],
    queryFn: () => api.getSession(sessionId || '').then(res => res.data.messages || []),
    enabled: !!sessionId,
    refetchInterval: 1000, // Simple polling for updates
    placeholderData: (previousData) => previousData, // Keep previous data while fetching to prevent flash
  });

  // Create Session Mutation
  const createSessionMutation = useMutation({
    mutationFn: (data: any) => api.createSession(data),
    onSuccess: (res) => {
      setSessionId(res.data.id);
      queryClient.invalidateQueries({ queryKey: ['sessions'] });
    }
  });

  // Send Message Mutation
  const sendMessageMutation = useMutation({
    mutationFn: (data: any) => api.sendMessage(sessionId || '', data),
    onMutate: async (newData) => {
      // Cancel outgoing refetches so they don't overwrite optimistic update
      await queryClient.cancelQueries({ queryKey: ['messages', sessionId] });

      // Snapshot previous value
      const previousMessages = queryClient.getQueryData(['messages', sessionId]);

      // Optimistically update to new value
      queryClient.setQueryData(['messages', sessionId], (old: any[] = []) => [
        ...old,
        {
          id: 'temp-' + Date.now(),
          role: 'user',
          content: newData.message,
          created_at: new Date().toISOString(),
        },
      ]);
      
      // Clear input immediately
      setInput('');
      setIsAutoScrolling(true);

      return { previousMessages };
    },
    onError: (err, newTodo, context) => {
      // Rollback on error
      queryClient.setQueryData(['messages', sessionId], context?.previousMessages);
      alert('Failed to send message. Please try again.');
    },
    onSuccess: (data, variables, context) => {
        // Manually update cache with the server response to prevent flicker
        // The server returns the Assistant message. The User message is already optimistically added.
        // We need to ensure the user message stays (maybe replace temp ID) and add assistant msg.
        // However, simply invalidating is cleaner IF the fetch is fast enough. 
        // To avoid the "disappear", we can APPEND the new assistant message to the cache before invalidating.
        
        queryClient.setQueryData(['messages', sessionId], (old: any[] = []) => {
            // We assume the user message is already there from onMutate. 
            // We just append the assistant message from the response data.
            return [...old, data.data];
        });
    },
    onSettled: () => {
      // Refetch after error or success to get real server data
      queryClient.invalidateQueries({ queryKey: ['messages', sessionId] });
    },
  });

  // Initialize Session
  useEffect(() => {
    if (agent && !sessionId) {
      startNewChat();
    }
  }, [agent]);

  // Scroll handling
  useEffect(() => {
    if (isAutoScrolling && messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isAutoScrolling, sendMessageMutation.isPending]); // Add isPending to scroll when typing indicator appears

  const startNewChat = () => {
    if (!agent) return;
    createSessionMutation.mutate({
      title: `Tester Chat - ${new Date().toLocaleTimeString()}`,
      agent_id: agent.id
    });
  };

  const handleSend = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!input.trim() || !sessionId || sendMessageMutation.isPending) return;
    sendMessageMutation.mutate({ message: input });
  };

  if (agentLoading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <ArrowPathIcon className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  if (agentError || !agent) {
    return (
      <div className="flex flex-col items-center justify-center h-screen bg-gray-50 p-4 text-center">
        <ExclamationCircleIcon className="w-12 h-12 text-red-500 mb-2" />
        <h2 className="text-xl font-bold text-gray-800">Agent Not Found</h2>
        <p className="text-gray-600">The agent link might be invalid or expired.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-[100dvh] bg-white">
      {/* Header */}
      <header className="flex items-center justify-between px-4 py-3 bg-white border-b border-gray-200 sticky top-0 z-10 shadow-sm">
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
                onClick={() => setShowReasoning(!showReasoning)}
                className={`p-2 rounded-full transition-colors ${showReasoning ? 'bg-purple-100 text-purple-600' : 'text-gray-400 hover:bg-gray-100'}`}
                title="Toggle Reasoning"
            >
                {showReasoning ? <EyeIcon className="w-5 h-5" /> : <EyeSlashIcon className="w-5 h-5" />}
            </button>
            <button
                onClick={startNewChat}
                className="p-2 rounded-full bg-gray-100 text-gray-600 hover:bg-gray-200 transition-colors"
                title="New Chat"
            >
                <PlusIcon className="w-5 h-5" />
            </button>
        </div>
      </header>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6 bg-gray-50" onScroll={() => setIsAutoScrolling(false)}>
        {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-gray-400 space-y-4 opacity-50">
                <ChatBubbleLeftRightIcon className="w-12 h-12" />
                <p>Start chatting with {agent.name}</p>
            </div>
        )}
        
        {messages.map((msg: any) => (
          <div key={msg.id} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
            <div
              className={`max-w-[85%] p-3.5 rounded-2xl text-sm leading-relaxed shadow-sm ${
                msg.role === 'user'
                  ? 'bg-blue-600 text-white rounded-br-none'
                  : 'bg-white text-gray-800 border border-gray-100 rounded-bl-none'
              }`}
            >
              <div className="whitespace-pre-wrap">{msg.content || (msg.reasoning_content ? "Thinking..." : "")}</div>
            </div>
            
            {/* Reasoning Content Bubble */}
            {msg.role === 'assistant' && msg.reasoning_content && showReasoning && (
                <div className="mt-2 max-w-[85%] p-3 rounded-xl bg-purple-50 border border-purple-100 text-xs text-purple-800">
                    <div className="flex items-center gap-1.5 mb-1 font-semibold text-purple-700 uppercase tracking-wider text-[10px]">
                        <ArrowPathIcon className="w-3 h-3" /> Reasoning Process
                    </div>
                    <div className="whitespace-pre-wrap leading-relaxed opacity-90">
                        {msg.reasoning_content}
                    </div>
                </div>
            )}
            
            <span className="text-[10px] text-gray-400 mt-1 px-1">
                {new Date(msg.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
            </span>
          </div>
        ))}
        
        {sendMessageMutation.isPending && (
            <div className="flex flex-col items-start animate-pulse w-full">
                 <div className="flex items-center gap-2 max-w-[85%] bg-white p-4 rounded-2xl rounded-bl-none shadow-sm border border-gray-100">
                    <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                    </div>
                    <span className="text-xs text-gray-400 font-medium">Agent is thinking...</span>
                 </div>
            </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-3 bg-white border-t border-gray-200 safe-area-bottom" style={{ paddingBottom: 'calc(0.75rem + env(safe-area-inset-bottom))' }}>
        <form
            onSubmit={handleSend}
            className="flex items-center gap-2 bg-gray-100 rounded-full px-4 py-2 focus-within:ring-2 focus-within:ring-blue-500 focus-within:bg-white transition-all shadow-inner"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type a message..."
            className="flex-1 bg-transparent border-none focus:ring-0 text-base h-9 placeholder-gray-400 text-gray-800"
            disabled={sendMessageMutation.isPending}
          />
          <button
            type="submit"
            disabled={!input.trim() || sendMessageMutation.isPending}
            className="p-2 rounded-full bg-blue-600 text-white disabled:opacity-50 disabled:bg-gray-400 hover:bg-blue-700 transition-all shadow-sm"
          >
            {sendMessageMutation.isPending ? <ArrowPathIcon className="w-5 h-5 animate-spin" /> : <PaperAirplaneIcon className="w-5 h-5" />}
          </button>
        </form>
      </div>
    </div>
  );
}
