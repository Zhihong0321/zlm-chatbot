import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { PlusIcon, ChatBubbleLeftRightIcon, ArrowLeftIcon, TrashIcon } from '@heroicons/react/24/outline';

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
    if (name === cookieName) {
      return value;
    }
  }
  return null;
};

const deleteUserCookie = (agentId: string) => {
  const cookieName = `chat_session_${agentId}`;
  document.cookie = `${cookieName}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/`;
};

export default function MobileTesterChatSessions() {
  const { agentId } = useParams();
  const navigate = useNavigate();
  
  const [sessions, setSessions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [agent, setAgent] = useState<any>(null);
  const [error, setError] = useState('');
  const [deletingSessionId, setDeletingSessionId] = useState<string | null>(null);

  // Load agent
  useEffect(() => {
    if (!agentId) return;
    
    api.getAgent(agentId)
      .then(res => {
        setAgent(res.data);
        setLoading(false);
      })
      .catch(err => {
        setError('Agent not found');
        setLoading(false);
      });
  }, [agentId]);

  // Load sessions for this agent
  useEffect(() => {
    if (!agent) return;
    
    loadSessions();
  }, [agent]);

  const loadSessions = async () => {
    try {
      // Get all sessions, then filter by agent
      const allSessions = await api.getSessions();
      const agentSessions = allSessions.data.filter((sess: any) => sess.agent_id === parseInt(agentId));
      setSessions(agentSessions.sort((a: any, b: any) => 
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      ));
    } catch (err) {
      console.error('Failed to load sessions:', err);
      setError('Failed to load sessions');
    }
  };

  const handleSessionClick = (session: any) => {
    setUserCookie(agentId!, session.id);
    navigate(`/tester/${agentId}/chat/${session.id}`);
  };

  const handleNewSession = async () => {
    try {
      const res = await api.createSession({
        title: 'New Chat',
        agent_id: agent!.id
      });
      const newSession = res.data;
      setUserCookie(agentId!, newSession.id);
      navigate(`/tester/${agentId}/chat/${newSession.id}`);
    } catch (err) {
      setError('Failed to create new session');
    }
  };

  const handleDeleteSession = async (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setDeletingSessionId(sessionId);
    
    try {
      await api.deleteSession(sessionId);
      await loadSessions();
      
      // If we deleted the current session in cookie, remove it
      const currentSessionId = getUserCookie(agentId!);
      if (currentSessionId === sessionId) {
        deleteUserCookie(agentId!);
      }
    } catch (err) {
      setError('Failed to delete session');
    } finally {
      setDeletingSessionId(null);
    }
  };

  const getSessionTitle = (session: any): string => {
    // Use last AI response as title, fallback to session title
    if (session.last_ai_response) {
      return session.last_ai_response.length > 50 
        ? session.last_ai_response.substring(0, 50) + '...'
        : session.last_ai_response;
    }
    return session.title || 'Untitled Chat';
  };

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      const today = new Date();
      const yesterday = new Date(today);
      yesterday.setDate(yesterday.getDate() - 1);
      
      if (date.toDateString() === today.toDateString()) {
        return 'Today';
      } else if (date.toDateString() === yesterday.toDateString()) {
        return 'Yesterday';
      } else {
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
      }
    } catch {
      return 'Unknown date';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <div className="text-gray-500">Loading sessions...</div>
      </div>
    );
  }

  if (error || !agent) {
    return (
      <div className="flex flex-col items-center justify-center h-screen bg-gray-50 p-4 text-center">
        <div className="text-red-500 mb-4">{error || 'Agent not found'}</div>
        <button 
          onClick={() => navigate('/')}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Go Home
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen bg-white">
      {/* Header */}
      <header className="flex items-center justify-between px-4 py-3 bg-white border-b border-gray-200 shrink-0">
        <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/')}
              className="p-2 rounded-full text-gray-600 hover:bg-gray-100"
            >
              <ArrowLeftIcon className="w-5 h-5" />
            </button>
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold shrink-0">
                {agent.name.charAt(0)}
            </div>
            <div>
                <h1 className="font-bold text-gray-900 text-lg">{agent.name}</h1>
                <p className="text-xs text-gray-500">Chat Sessions</p>
            </div>
        </div>
        <button
          onClick={handleNewSession}
          className="p-2 rounded-full bg-blue-600 text-white hover:bg-blue-700 transition-colors"
          title="New Chat"
        >
          <PlusIcon className="w-5 h-5" />
        </button>
      </header>

      {/* Sessions List */}
      <div className="flex-1 overflow-y-auto bg-gray-50">
        {sessions.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full p-8 text-center">
            <ChatBubbleLeftRightIcon className="w-16 h-16 text-gray-400 mb-4" />
            <h2 className="text-xl font-semibold text-gray-700 mb-2">No chat sessions yet</h2>
            <p className="text-gray-500 mb-6">Start a conversation to see your chat history here</p>
            <button
              onClick={handleNewSession}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
            >
              <PlusIcon className="w-5 h-5" />
              Start New Chat
            </button>
          </div>
        ) : (
          <div className="p-4 space-y-3">
            <div className="text-xs text-gray-500 uppercase tracking-wider px-2 pb-2">
              {sessions.length} {sessions.length === 1 ? 'Session' : 'Sessions'}
            </div>
            
            {sessions.map((session) => (
              <div
                key={session.id}
                onClick={() => handleSessionClick(session)}
                className="bg-white border border-gray-200 rounded-lg p-4 cursor-pointer hover:bg-gray-50 transition-colors group"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <h3 className="font-medium text-gray-900 truncate mb-1">
                      {getSessionTitle(session)}
                    </h3>
                    <p className="text-sm text-gray-500">
                      {formatDate(session.created_at)} • {session.message_count || 0} messages
                    </p>
                  </div>
                  <button
                    onClick={(e) => handleDeleteSession(session.id, e)}
                    disabled={deletingSessionId === session.id}
                    className="p-1 rounded-full text-gray-400 hover:text-red-500 hover:bg-red-50 opacity-0 group-hover:opacity-100 transition-all"
                    title="Delete session"
                  >
                    <TrashIcon className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
