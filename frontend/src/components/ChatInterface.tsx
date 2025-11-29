import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAgents, useSessions, useCreateSession, useSessionHistory, useSendMessage, useUploadFile, useUpdateSession } from '../hooks/useApi';
import { Agent, Message } from '../types';

export default function ChatInterface() {
  const { sessionId } = useParams<{ sessionId?: string }>();
  const navigate = useNavigate();
  
  const { data: agents } = useAgents();
  const { data: sessions } = useSessions();
  const createSessionMutation = useCreateSession();
  const sendMessageMutation = useSendMessage();
  const uploadFileMutation = useUploadFile();
  
  const { data: messages } = useSessionHistory(sessionId || '');
  
  const [message, setMessage] = useState('');
  const [selectedAgentId, setSelectedAgentId] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [showAgentInfo, setShowAgentInfo] = useState(false);
  const [editingMessageId, setEditingMessageId] = useState<string | null>(null);
  const [editingContent, setEditingContent] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const currentSession = sessions?.find(s => s.id === sessionId);
  const currentAgent = agents?.find(a => a.id === currentSession?.agent_id) || agents?.find(a => a.id === selectedAgentId);
  const updateSessionMutation = useUpdateSession();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(e as any);
    }
  };

  const handleAgentSwitch = async (newAgentId: string) => {
    if (!sessionId) return;
    
    try {
      await updateSessionMutation.mutateAsync({
        id: sessionId,
        agent_id: newAgentId
      });
    } catch (error) {
      console.error('Failed to switch agent:', error);
    }
  };

  const handleEditMessage = (messageId: string, content: string) => {
    setEditingMessageId(messageId);
    setEditingContent(content);
  };

  const handleSaveEdit = () => {
    // This would need an update message API endpoint
    setEditingMessageId(null);
    setEditingContent('');
  };

  const handleCancelEdit = () => {
    setEditingMessageId(null);
    setEditingContent('');
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: true 
    });
  };

  const copyMessage = (content: string) => {
    navigator.clipboard.writeText(content);
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim() || isLoading) return;

    let targetSessionId = sessionId;
    
    // Create new session if none exists
    if (!targetSessionId) {
      try {
        const newSession = await createSessionMutation.mutateAsync({
          title: message.slice(0, 50) + (message.length > 50 ? '...' : ''),
          agent_id: selectedAgentId || undefined,
        });
        targetSessionId = newSession.id;
        navigate(`/chat/${targetSessionId}`, { replace: true });
      } catch (error) {
        console.error('Failed to create session:', error);
        return;
      }
    }

    setIsLoading(true);
    setIsTyping(true);
    try {
      await sendMessageMutation.mutateAsync({
        sessionId: targetSessionId,
        message: message.trim(),
      });
      setMessage('');
      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setIsLoading(false);
      setIsTyping(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !sessionId) return;

    // Check file size (50KB limit)
    if (file.size > 50 * 1024) {
      alert('File size must be less than 50KB');
      return;
    }

    try {
      await uploadFileMutation.mutateAsync({
        sessionId,
        file,
      });
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (error) {
      console.error('Failed to upload file:', error);
      alert('Failed to upload file');
    }
  };

  return (
    <div className="h-screen flex flex-col bg-white">
      <div className="border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h2 className="text-lg font-semibold text-gray-900">
              {currentSession?.title || 'New Chat'}
            </h2>
            
            {/* Agent Selection and Display */}
            <div className="flex items-center space-x-2">
              {currentAgent && (
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600">Agent:</span>
                  <button
                    onClick={() => setShowAgentInfo(!showAgentInfo)}
                    className="px-2 py-1 text-sm bg-blue-100 hover:bg-blue-200 text-blue-800 rounded-md flex items-center space-x-1"
                  >
                    <span>{currentAgent.name}</span>
                    <span className="text-xs text-blue-600">({currentAgent.model})</span>
                  </button>
                  {showAgentInfo && (
                    <div className="absolute top-16 left-4 z-10 bg-white border border-gray-200 rounded-lg shadow-lg p-4 max-w-sm">
                      <h3 className="font-medium text-gray-900 mb-2">{currentAgent.name}</h3>
                      <p className="text-sm text-gray-600 mb-2">{currentAgent.description}</p>
                      <p className="text-xs text-gray-500">Model: {currentAgent.model}</p>
                      <p className="text-xs text-gray-500">Temperature: {currentAgent.temperature}</p>
                      <div className="mt-2">
                        <p className="text-xs font-medium text-gray-700">System Prompt:</p>
                        <p className="text-xs text-gray-600 mt-1 whitespace-pre-wrap">{currentAgent.system_prompt.slice(0, 100)}...</p>
                      </div>
                    </div>
                  )}
                </div>
              )}
              
              {/* Agent Switcher for existing sessions */}
              {sessionId && agents && (
                <select
                  value={currentSession?.agent_id || ''}
                  onChange={(e) => handleAgentSwitch(e.target.value)}
                  className="px-2 py-1 text-xs border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Switch Agent</option>
                  {agents.map((agent: Agent) => (
                    <option key={agent.id} value={agent.id}>
                      {agent.name}
                    </option>
                  ))}
                </select>
              )}
              
              {/* Agent Selector for new sessions */}
              {!sessionId && agents && (
                <select
                  value={selectedAgentId}
                  onChange={(e) => setSelectedAgentId(e.target.value)}
                  className="px-3 py-1 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select Agent</option>
                  {agents.map((agent: Agent) => (
                    <option key={agent.id} value={agent.id}>
                      {agent.name}
                    </option>
                  ))}
                </select>
              )}
            </div>
          </div>
          
          {sessionId && (
            <div className="flex items-center space-x-2">
              <input
                ref={fileInputRef}
                type="file"
                onChange={handleFileUpload}
                className="hidden"
                accept=".txt,.md,.json,.csv"
              />
              <button
                onClick={() => fileInputRef.current?.click()}
                disabled={uploadFileMutation.isPending}
                className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-md disabled:opacity-50"
              >
                {uploadFileMutation.isPending ? 'Uploading...' : 'Upload File'}
              </button>
              <button
                onClick={() => navigate('/')}
                className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-md"
              >
                Back to Dashboard
              </button>
            </div>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-6 py-4">
        {messages && messages.length > 0 ? (
          <div className="space-y-4">
            {messages.map((msg: Message) => (
              <div
                key={msg.id}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} group`}
              >
                <div
                  className={`max-w-2xl px-4 py-2 rounded-lg relative ${
                    msg.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  {editingMessageId === msg.id ? (
                    <div className="space-y-2">
                      <textarea
                        value={editingContent}
                        onChange={(e) => setEditingContent(e.target.value)}
                        className="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        rows={3}
                      />
                      <div className="flex space-x-2">
                        <button
                          onClick={handleSaveEdit}
                          className="px-2 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700"
                        >
                          Save
                        </button>
                        <button
                          onClick={handleCancelEdit}
                          className="px-2 py-1 text-xs bg-gray-600 text-white rounded hover:bg-gray-700"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <>
                      <p className="whitespace-pre-wrap">{msg.content}</p>
                      
                      {/* Message metadata and actions */}
                      <div className={`flex items-center justify-between mt-2 ${
                        msg.role === 'user' ? 'text-blue-100' : 'text-gray-500'
                      }`}>
                        <span className="text-xs">
                          {formatTimestamp(msg.timestamp)}
                          {msg.token_usage && ` • ${msg.token_usage.total_tokens} tokens`}
                        </span>
                        
                        {/* Action buttons */}
                        <div className="flex space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                          <button
                            onClick={() => copyMessage(msg.content)}
                            className="p-1 hover:bg-gray-200 rounded text-xs"
                            title="Copy message"
                          >
                            📋
                          </button>
                          {msg.role === 'user' && (
                            <button
                              onClick={() => handleEditMessage(msg.id, msg.content)}
                              className="p-1 hover:bg-gray-200 rounded text-xs"
                              title="Edit message"
                            >
                              ✏️
                            </button>
                          )}
                        </div>
                      </div>
                    </>
                  )}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        ) : (
          <div className="text-center text-gray-500 mt-8">
            <p>No messages yet. Start a conversation!</p>
            {currentAgent && (
              <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg max-w-md mx-auto">
                <p className="text-sm text-blue-800">
                  <span className="font-medium">{currentAgent.name}</span> is ready to help!
                </p>
                <p className="text-xs text-blue-600 mt-1">{currentAgent.description}</p>
              </div>
            )}
          </div>
        )}
        
        {/* Typing Indicator */}
        {isTyping && !isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 text-gray-900 max-w-2xl px-4 py-2 rounded-lg">
              <div className="flex items-center space-x-2">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                </div>
                <span className="text-sm text-gray-600">Thinking...</span>
              </div>
            </div>
          </div>
        )}
        
        {/* Loading Indicator */}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 text-gray-900 max-w-2xl px-4 py-2 rounded-lg">
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600"></div>
                <span>Processing...</span>
              </div>
            </div>
          </div>
        )}
      </div>

      <form onSubmit={handleSendMessage} className="border-t border-gray-200 px-6 py-4">
        <div className="flex space-x-4">
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={message}
              onChange={(e) => {
                setMessage(e.target.value);
                // Auto-resize textarea
                e.target.style.height = 'auto';
                e.target.style.height = `${Math.min(e.target.scrollHeight, 200)}px`;
              }}
              onKeyDown={handleKeyPress}
              placeholder="Type your message... (Enter to send, Shift+Enter for new line)"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
              disabled={isLoading}
              rows={1}
              style={{ minHeight: '44px', maxHeight: '200px' }}
            />
            <div className="absolute bottom-2 right-2 text-xs text-gray-400">
              {message.length} / 2000
            </div>
          </div>
          <button
            type="submit"
            disabled={!message.trim() || isLoading || message.length > 2000}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed self-end"
          >
            Send
          </button>
        </div>
        
        {/* Character count warning */}
        {message.length > 1800 && (
          <div className="mt-1 text-xs text-amber-600">
            ⚠️ Approaching message length limit
          </div>
        )}
      </form>
    </div>
  );
}