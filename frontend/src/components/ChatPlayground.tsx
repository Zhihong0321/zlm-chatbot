import React, { useState, useEffect } from 'react';
import { useAgents, useCreateSession, useSendMessage } from '../hooks/useApi';
import { Agent } from '../types';

export default function ChatPlayground() {
  const { data: agents } = useAgents();
  const createSessionMutation = useCreateSession();
  const sendMessageMutation = useSendMessage();
  
  const [selectedAgentId, setSelectedAgentId] = useState('');
  const [message, setMessage] = useState('');
  const [response, setResponse] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [testSessions, setTestSessions] = useState<Array<{id: string, agentId: string, question: string, response: string, timestamp: string}>>([]);

  const handleTest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim() || isLoading) return;

    setIsLoading(true);
    try {
      // Create temporary session for testing
      const tempSession = await createSessionMutation.mutateAsync({
        title: 'Test Session',
        agent_id: selectedAgentId || undefined,
      });
      
      const startTime = new Date().toISOString();
      
      // Send message and get response
      const result = await sendMessageMutation.mutateAsync({
        sessionId: tempSession.id,
        message: message.trim(),
      });
      
      const responseText = result.content || 'No response received';
      setResponse(responseText);
      
      // Add to test history
      setTestSessions(prev => [{
        id: tempSession.id,
        agentId: selectedAgentId,
        question: message.trim(),
        response: responseText,
        timestamp: startTime
      }, ...prev].slice(0, 5)); // Keep only last 5 tests
    } catch (error) {
      console.error('Test failed:', error);
      setResponse('Error: ' + (error as Error).message);
    } finally {
      setIsLoading(false);
    }
  };

  const clearHistory = () => {
    setTestSessions([]);
    setResponse('');
  };

  const loadTestQuestion = (question: string) => {
    setMessage(question);
  };

  const selectedAgent = agents?.find(a => a.id === selectedAgentId);

  // Pre-defined test questions
  const testQuestions = [
    "What can you help me with?",
    "Explain quantum computing simply",
    "Write a Python function to calculate factorial",
    "Help me brainstorm ideas for a project",
    "What's the weather like today?"
  ];

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="border-4 border-dashed border-gray-200 rounded-lg p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Agent Playground</h1>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div>
              <label htmlFor="agent" className="block text-sm font-medium text-gray-700 mb-1">
                Select Agent
              </label>
              <select
                id="agent"
                value={selectedAgentId}
                onChange={(e) => setSelectedAgentId(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Choose an agent...</option>
                {agents?.map((agent: Agent) => (
                  <option key={agent.id} value={agent.id}>
                    {agent.name} ({agent.model})
                  </option>
                ))}
              </select>
            </div>

            {selectedAgent && (
              <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
                <h3 className="font-medium text-blue-900 mb-2">{selectedAgent.name}</h3>
                <p className="text-sm text-blue-700 mb-1">{selectedAgent.description}</p>
                <p className="text-xs text-blue-600">
                  Model: {selectedAgent.model} | Temperature: {selectedAgent.temperature}
                </p>
                <div className="mt-2">
                  <p className="text-xs text-blue-600 font-medium">System Prompt:</p>
                  <p className="text-xs text-blue-700 mt-1 whitespace-pre-wrap">{selectedAgent.system_prompt}</p>
                </div>
              </div>
            )}

            <form onSubmit={handleTest} className="space-y-4">
              <div>
                <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-1">
                  Test Message
                </label>
                <textarea
                  id="message"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Enter a test message..."
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isLoading}
                />
              </div>

              <button
                type="submit"
                disabled={!message.trim() || !selectedAgentId || isLoading}
                className="w-full px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? 'Testing...' : 'Test Agent'}
              </button>
            </form>
            
            {/* Test History */}
            {testSessions.length > 0 && (
              <div className="mt-4">
                <div className="flex justify-between items-center mb-2">
                  <h3 className="text-sm font-medium text-gray-700">Recent Tests</h3>
                  <button
                    onClick={clearHistory}
                    className="text-xs text-red-600 hover:text-red-800"
                  >
                    Clear History
                  </button>
                </div>
                <div className="space-y-2 max-h-40 overflow-y-auto">
                  {testSessions.map((session, index) => {
                    const agent = agents?.find(a => a.id === session.agentId);
                    return (
                      <div key={session.id} className="bg-gray-50 border border-gray-200 rounded-md p-2">
                        <div className="flex justify-between items-start mb-1">
                          <span className="text-xs font-medium text-gray-700">
                            {agent?.name || 'Unknown Agent'}
                          </span>
                          <span className="text-xs text-gray-500">
                            {new Date(session.timestamp).toLocaleTimeString()}
                          </span>
                        </div>
                        <p className="text-xs text-gray-600 truncate">{session.question}</p>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
            
            {/* Test History */}
            {testSessions.length > 0 && (
              <div className="mt-4">
                <div className="flex justify-between items-center mb-2">
                  <h3 className="text-sm font-medium text-gray-700">Recent Tests</h3>
                  <button
                    onClick={clearHistory}
                    className="text-xs text-red-600 hover:text-red-800"
                  >
                    Clear History
                  </button>
                </div>
                <div className="space-y-2 max-h-40 overflow-y-auto">
                  {testSessions.map((session, index) => {
                    const agent = agents?.find(a => a.id === session.agentId);
                    return (
                      <div key={session.id} className="bg-gray-50 border border-gray-200 rounded-md p-2">
                        <div className="flex justify-between items-start mb-1">
                          <span className="text-xs font-medium text-gray-700">
                            {agent?.name || 'Unknown Agent'}
                          </span>
                          <span className="text-xs text-gray-500">
                            {new Date(session.timestamp).toLocaleTimeString()}
                          </span>
                        </div>
                        <p className="text-xs text-gray-600 truncate">{session.question}</p>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>

          <div className="space-y-4">
            <h2 className="text-lg font-medium text-gray-900">Response</h2>
            
            {isLoading ? (
              <div className="flex items-center justify-center h-64 bg-gray-50 border border-gray-200 rounded-lg">
                <div className="text-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600 mx-auto mb-2"></div>
                  <p className="text-gray-600">Processing request...</p>
                  {selectedAgent && (
                    <p className="text-xs text-gray-500 mt-1">Testing with {selectedAgent.name}</p>
                  )}
                </div>
              </div>
            ) : response ? (
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-medium text-gray-900">Agent Response</h3>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => navigator.clipboard.writeText(response)}
                      className="text-xs px-2 py-1 bg-gray-200 hover:bg-gray-300 rounded text-gray-700"
                    >
                      Copy
                    </button>
                  </div>
                </div>
                <div className="whitespace-pre-wrap text-gray-700 max-h-96 overflow-y-auto">{response}</div>
                
                {/* Response metadata */}
                {testSessions.length > 0 && testSessions[0].response === response && (
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <div className="flex justify-between items-center text-xs text-gray-500">
                      <span>Agent: {selectedAgent?.name}</span>
                      <span>Model: {selectedAgent?.model}</span>
                      <span>Temperature: {selectedAgent?.temperature}</span>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center justify-center h-64 bg-gray-50 border border-gray-200 rounded-lg">
                <div className="text-center">
                  <p className="text-gray-500 mb-2">Select an agent and send a test message to see the response</p>
                  {agents && agents.length === 0 && (
                    <p className="text-xs text-gray-400">No agents available. Create an agent first.</p>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}