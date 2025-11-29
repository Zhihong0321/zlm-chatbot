import { useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { useSessions, useDeleteSession, useSearchSessions, useBulkDeleteSessions, useArchiveSession } from '../hooks/useApi';
import { formatDistanceToNow } from 'date-fns';
import AnalyticsPanel from './AnalyticsPanel';

export default function SessionDashboard() {
  const { data: sessions, isLoading, error } = useSessions();
  const deleteSessionMutation = useDeleteSession();
  const searchSessionsMutation = useSearchSessions();
  const bulkDeleteMutation = useBulkDeleteSessions();
  const archiveSessionMutation = useArchiveSession();
  
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState<'date' | 'messages' | 'title'>('date');
  const [selectedSessions, setSelectedSessions] = useState<string[]>([]);
  const [showBulkActions, setShowBulkActions] = useState(false);
  const [showAdvancedSearch, setShowAdvancedSearch] = useState(false);
  const [showAnalytics, setShowAnalytics] = useState(false);
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  // Advanced search filters
  const [searchFilters, setSearchFilters] = useState({
    agent_id: '',
    date_from: '',
    date_to: '',
    min_messages: ''
  });

  const handleDeleteSession = async (sessionId: string) => {
    if (window.confirm('Are you sure you want to delete this session?')) {
      try {
        await deleteSessionMutation.mutateAsync(sessionId);
      } catch (error) {
        console.error('Failed to delete session:', error);
      }
    }
  };

  const handleArchiveSession = async (sessionId: string) => {
    try {
      await archiveSessionMutation.mutateAsync(sessionId);
    } catch (error) {
      console.error('Failed to archive session:', error);
    }
  };

  const handleBulkDelete = async () => {
    if (window.confirm(`Are you sure you want to delete ${selectedSessions.length} sessions?`)) {
      try {
        await bulkDeleteMutation.mutateAsync(selectedSessions);
        setSelectedSessions([]);
        setShowBulkActions(false);
      } catch (error) {
        console.error('Failed to delete sessions:', error);
      }
    }
  };

  const handleBulkArchive = async () => {
    try {
      await Promise.all(
        selectedSessions.map(sessionId => archiveSessionMutation.mutateAsync(sessionId))
      );
      setSelectedSessions([]);
      setShowBulkActions(false);
    } catch (error) {
      console.error('Failed to archive sessions:', error);
    }
  };

  const handleSearch = async () => {
    if (searchTerm.trim() || Object.values(searchFilters).some(val => val)) {
      setIsSearching(true);
      try {
        const params = {
          ...(searchTerm && { q: searchTerm }),
          ...(searchFilters.agent_id && { agent_id: parseInt(searchFilters.agent_id) }),
          ...(searchFilters.date_from && { date_from: searchFilters.date_from }),
          ...(searchFilters.date_to && { date_to: searchFilters.date_to }),
          ...(searchFilters.min_messages && { min_messages: parseInt(searchFilters.min_messages) })
        };
        
        const results = await searchSessionsMutation.mutateAsync(params);
        setSearchResults(results);
      } catch (error) {
        console.error('Search failed:', error);
        setSearchResults([]);
      } finally {
        setIsSearching(false);
      }
    } else {
      setSearchResults([]);
    }
  };

  const clearSearch = () => {
    setSearchTerm('');
    setSearchFilters({
      agent_id: '',
      date_from: '',
      date_to: '',
      min_messages: ''
    });
    setSearchResults([]);
    setIsSearching(false);
  };

  const handleSelectSession = (sessionId: string) => {
    setSelectedSessions(prev => 
      prev.includes(sessionId) 
        ? prev.filter(id => id !== sessionId)
        : [...prev, sessionId]
    );
  };

  const handleSelectAll = () => {
    if (selectedSessions.length === filteredSessions.length) {
      setSelectedSessions([]);
    } else {
      setSelectedSessions(filteredSessions.map(s => s.id));
    }
  };

  const filteredSessions = useMemo(() => {
    const sessionList = isSearching ? searchResults : (sessions || []);
    
    let filtered = sessionList.filter((session: any) =>
      session.title.toLowerCase().includes(searchTerm.toLowerCase())
    );

    // Sort sessions
    filtered.sort((a: any, b: any) => {
      switch (sortBy) {
        case 'date':
          return new Date(b.updated_at || b.created_at).getTime() - new Date(a.updated_at || a.created_at).getTime();
        case 'messages':
          return (b.message_count || 0) - (a.message_count || 0);
        case 'title':
          return a.title.localeCompare(b.title);
        default:
          return 0;
      }
    });

    return filtered;
  }, [sessions, searchResults, searchTerm, sortBy, isSearching]);

  const exportSession = (session: any) => {
    const dataStr = JSON.stringify(session, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `session-${session.id}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <p className="text-red-700">Error loading sessions: {error.message}</p>
      </div>
    );
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="border-4 border-dashed border-gray-200 rounded-lg p-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Chat Sessions</h1>
          <div className="flex space-x-2">
            <button
              onClick={() => setShowAnalytics(!showAnalytics)}
              className={`px-4 py-2 rounded-md font-medium transition-colors ${
                showAnalytics 
                  ? 'bg-purple-600 hover:bg-purple-700 text-white' 
                  : 'bg-gray-200 hover:bg-gray-300 text-gray-700'
              }`}
            >
              📊 Analytics
            </button>
            <Link
              to="/chat"
              className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md"
            >
              New Chat
            </Link>
          </div>
        </div>

        {/* Analytics Panel */}
        {showAnalytics && (
          <AnalyticsPanel className="mb-6" />
        )}

        {/* Search and Filter Controls */}
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-6">
          <div className="flex flex-col space-y-4">
            {/* Basic Search */}
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <input
                  type="text"
                  placeholder="Search sessions..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="flex gap-2">
                <button
                  onClick={handleSearch}
                  disabled={isSearching}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md disabled:opacity-50"
                >
                  {isSearching ? 'Searching...' : 'Search'}
                </button>
                <button
                  onClick={() => setShowAdvancedSearch(!showAdvancedSearch)}
                  className="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-md"
                >
                  {showAdvancedSearch ? 'Simple' : 'Advanced'}
                </button>
                {(isSearching || searchResults.length > 0) && (
                  <button
                    onClick={clearSearch}
                    className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-md"
                  >
                    Clear
                  </button>
                )}
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as any)}
                  className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="date">Sort by Date</option>
                  <option value="messages">Sort by Messages</option>
                  <option value="title">Sort by Title</option>
                </select>
              </div>
            </div>
            
            {/* Advanced Search */}
            {showAdvancedSearch && (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 pt-4 border-t border-gray-200">
                <input
                  type="number"
                  placeholder="Agent ID"
                  value={searchFilters.agent_id}
                  onChange={(e) => setSearchFilters({...searchFilters, agent_id: e.target.value})}
                  className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <input
                  type="date"
                  placeholder="Date From"
                  value={searchFilters.date_from}
                  onChange={(e) => setSearchFilters({...searchFilters, date_from: e.target.value})}
                  className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <input
                  type="date"
                  placeholder="Date To"
                  value={searchFilters.date_to}
                  onChange={(e) => setSearchFilters({...searchFilters, date_to: e.target.value})}
                  className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <input
                  type="number"
                  placeholder="Min Messages"
                  value={searchFilters.min_messages}
                  onChange={(e) => setSearchFilters({...searchFilters, min_messages: e.target.value})}
                  className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            )}
          </div>
          
          {/* Bulk Actions */}
          {showBulkActions && selectedSessions.length > 0 && (
            <div className="flex justify-between items-center mt-4 pt-4 border-t border-gray-200">
              <div className="flex items-center space-x-4">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={selectedSessions.length === filteredSessions.length}
                    onChange={handleSelectAll}
                    className="mr-2"
                  />
                  <span className="text-sm text-gray-700">
                    {selectedSessions.length} of {filteredSessions.length} selected
                  </span>
                </label>
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={handleBulkArchive}
                  className="px-3 py-1 bg-yellow-600 hover:bg-yellow-700 text-white rounded-md text-sm"
                >
                  Archive Selected
                </button>
                <button
                  onClick={handleBulkDelete}
                  className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white rounded-md text-sm"
                >
                  Delete Selected
                </button>
                <button
                  onClick={() => setSelectedSessions([])}
                  className="px-3 py-1 bg-gray-600 hover:bg-gray-700 text-white rounded-md text-sm"
                >
                  Clear Selection
                </button>
              </div>
            </div>
          )}
          
          {sessions && sessions.length > 0 && !isSearching && (
            <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-200">
              <span className="text-sm text-gray-600">
                {filteredSessions.length} sessions found
              </span>
              <button
                onClick={() => setShowBulkActions(!showBulkActions)}
                className="px-3 py-2 bg-gray-200 hover:bg-gray-300 rounded-md text-sm"
              >
                {showBulkActions ? 'Cancel' : 'Select'}
              </button>
            </div>
          )}
        </div>

        {(!sessions || sessions.length === 0) && !isSearching ? (
          <div className="text-center py-12">
            <p className="text-gray-500 mb-4">No chat sessions yet.</p>
            <Link
              to="/chat"
              className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md"
            >
              Start Your First Chat
            </Link>
          </div>
        ) : filteredSessions.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500 mb-4">
              {isSearching ? 'No sessions found matching your search criteria' : 'No sessions found'}
            </p>
            {isSearching ? (
              <button
                onClick={clearSearch}
                className="bg-gray-600 hover:bg-gray-700 text-white font-medium py-2 px-4 rounded-md"
              >
                Clear Search
              </button>
            ) : (
              <button
                onClick={() => setSearchTerm('')}
                className="bg-gray-600 hover:bg-gray-700 text-white font-medium py-2 px-4 rounded-md"
              >
                Clear Search
              </button>
            )}
          </div>
        ) : (
          <>
            <div className="mb-4 text-sm text-gray-600">
              {isSearching 
                ? `Found ${filteredSessions.length} session${filteredSessions.length !== 1 ? 's' : ''}`
                : `Showing ${filteredSessions.length} of ${sessions.length} sessions`
              }
            </div>
            
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {filteredSessions.map((session) => (
                <div
                  key={session.id}
                  className="bg-white border border-gray-200 rounded-lg shadow-sm p-4 hover:shadow-md transition-shadow relative"
                >
                  {showBulkActions && (
                    <div className="absolute top-2 left-2">
                      <input
                        type="checkbox"
                        checked={selectedSessions.includes(session.id)}
                        onChange={() => handleSelectSession(session.id)}
                        className="rounded border-gray-300"
                      />
                    </div>
                  )}
                  
                  <div className={`flex justify-between items-start mb-2 ${showBulkActions ? 'ml-6' : ''}`}>
                    <h3 className="text-lg font-medium text-gray-900 truncate">
                      {session.title}
                    </h3>
                    <div className="flex space-x-1">
                      <button
                        onClick={() => exportSession(session)}
                        className="text-gray-400 hover:text-gray-600 text-sm"
                        title="Export session"
                      >
                        📥
                      </button>
                      <button
                        onClick={() => handleArchiveSession(session.id)}
                        className="text-yellow-500 hover:text-yellow-700 text-sm"
                        title="Archive session"
                      >
                        📁
                      </button>
                      <button
                        onClick={() => handleDeleteSession(session.id)}
                        className="text-red-500 hover:text-red-700 text-sm"
                        title="Delete session"
                      >
                        🗑️
                      </button>
                    </div>
                  </div>
                  
                  <div className="space-y-1 mb-3">
                    <p className="text-sm text-gray-500">
                      📊 {(session.message_count || 0)} messages
                    </p>
                    <p className="text-xs text-gray-400">
                      🕒 {formatDistanceToNow(new Date(session.created_at), { addSuffix: true })}
                    </p>
                    <p className="text-xs text-gray-400">
                      🔄 Updated {formatDistanceToNow(new Date(session.updated_at || session.created_at), { addSuffix: true })}
                    </p>
                    {session.is_archived && (
                      <p className="text-xs text-yellow-600 font-medium">
                        📁 Archived
                      </p>
                    )}
                  </div>
                  
                  <Link
                    to={`/chat/${session.id}`}
                    className="block w-full text-center bg-blue-50 hover:bg-blue-100 text-blue-600 font-medium py-2 px-4 rounded-md"
                  >
                    Open Chat
                  </Link>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}