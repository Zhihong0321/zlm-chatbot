import React, { useState, useRef } from 'react';
import { useAgents, useCreateAgent, useUpdateAgent, useDeleteAgent, useUploadAgentFile, useDeleteAgentFile, useAgentWithFiles } from '../hooks/useApi';
import type { Agent, AgentKnowledgeFile } from '../types';

export default function AgentBuilder() {
  const { data: agents, isLoading, error } = useAgents();
  const createAgentMutation = useCreateAgent();
  const updateAgentMutation = useUpdateAgent();
  const deleteAgentMutation = useDeleteAgent();
  const uploadFileMutation = useUploadAgentFile();
  const deleteFileMutation = useDeleteAgentFile();
  
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    model: 'glm-4.6',
    system_prompt: '',
    temperature: 0.7,
  });

  const [isFormVisible, setIsFormVisible] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [expandedAgentId, setExpandedAgentId] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      model: 'glm-4.6',
      system_prompt: '',
      temperature: 0.7,
    });
    setEditingId(null);
    setIsFormVisible(false);
  };

  const handleCreateClick = () => {
    setEditingId(null);
    setFormData({
      name: '',
      description: '',
      model: 'glm-4.6',
      system_prompt: '',
      temperature: 0.7,
    });
    setIsFormVisible(true);
  };

  const handleEditClick = (agent: any) => {
    setEditingId(agent.id);
    setFormData({
      name: agent.name,
      description: agent.description || '',
      model: agent.model,
      system_prompt: agent.system_prompt,
      temperature: agent.temperature,
    });
    setIsFormVisible(true);
  };

  const handleDeleteClick = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this agent?')) {
      try {
        await deleteAgentMutation.mutateAsync(id);
      } catch (error) {
        console.error('Failed to delete agent:', error);
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingId) {
        await updateAgentMutation.mutateAsync({ id: editingId, data: formData });
      } else {
        await createAgentMutation.mutateAsync(formData);
      }
      resetForm();
    } catch (error) {
      console.error('Failed to save agent:', error);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'temperature' ? parseFloat(value) : value,
    }));
  };

  const handleFileUpload = async (agentId: string, e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      await uploadFileMutation.mutateAsync({ agentId, file, purpose: 'agent' });
      // Clear file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (error) {
      console.error('Failed to upload file:', error);
    }
  };

  const handleDeleteFile = async (agentId: string, fileId: string) => {
    try {
      await deleteFileMutation.mutateAsync({ agentId, fileId });
    } catch (error) {
      console.error('Failed to delete file:', error);
    }
  };

  const toggleFilesSection = (agentId: string) => {
    setExpandedAgentId(expandedAgentId === agentId ? null : agentId);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (fileType: string) => {
    switch (fileType) {
      case 'pdf':
        return '📄';
      case 'doc':
      case 'docx':
        return '📝';
      case 'txt':
        return '📃';
      case 'jpg':
      case 'jpeg':
      case 'png':
        return '🖼️';
      default:
        return '📎';
    }
  };

  // Component for Agent Files Management
  const AgentFilesSection = ({ agentId }: { agentId: string }) => {
    const { data: agentWithFiles, isLoading: filesLoading } = useAgentWithFiles(agentId);

    return (
      <div className="mt-4 border-t border-gray-100 pt-4">
        <div className="flex items-center justify-between mb-3">
          <h4 className="text-sm font-medium text-gray-700">Knowledge Files</h4>
          <div className="flex space-x-2">
            <input
              ref={fileInputRef}
              type="file"
              accept=".txt,.pdf,.doc,.docx,.xlsx,.ppt,.pptx,.jpg,.jpeg,.png"
              onChange={(e) => handleFileUpload(agentId, e)}
              className="hidden"
              id={`file-upload-${agentId}`}
            />
            <label
              htmlFor={`file-upload-${agentId}`}
              className="text-xs bg-blue-50 text-blue-600 px-2 py-1 rounded cursor-pointer hover:bg-blue-100 transition-colors"
            >
              {uploadFileMutation.isPending ? 'Uploading...' : 'Upload File'}
            </label>
          </div>
        </div>
        
        {filesLoading ? (
          <div className="text-sm text-gray-500">Loading files...</div>
        ) : agentWithFiles?.knowledge_files?.length > 0 ? (
          <div className="space-y-2">
            {agentWithFiles.knowledge_files.map((file) => (
              <div
                key={file.id}
                className="flex items-center justify-between bg-gray-50 rounded p-2 text-xs"
              >
                <div className="flex items-center space-x-2 flex-1 min-w-0">
                  <span className="text-lg">{getFileIcon(file.file_type)}</span>
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-gray-900 truncate" title={file.original_filename}>
                      {file.original_filename}
                    </div>
                    <div className="text-gray-500">
                      {formatFileSize(file.file_size)} • {file.file_type.toUpperCase()}
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => handleDeleteFile(agentId, file.id)}
                  className="text-red-500 hover:text-red-700 px-1 py-0.5"
                  title="Delete file"
                  disabled={deleteFileMutation.isPending}
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-sm text-gray-500 italic">No knowledge files uploaded</div>
        )}
      </div>
    );
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="border-4 border-dashed border-gray-200 rounded-lg p-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Agent Builder</h1>
          <button
            onClick={() => isFormVisible ? resetForm() : handleCreateClick()}
            className={`${isFormVisible ? 'bg-gray-600 hover:bg-gray-700' : 'bg-green-600 hover:bg-green-700'} text-white font-medium py-2 px-4 rounded-md`}
          >
            {isFormVisible ? 'Cancel' : 'Create Agent'}
          </button>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
            <p className="text-red-700">Error loading agents: {error.message}</p>
          </div>
        )}

        {isFormVisible && (
          <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">
              {editingId ? 'Edit Agent' : 'Create New Agent'}
            </h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
                  Name
                </label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <input
                  type="text"
                  id="description"
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label htmlFor="model" className="block text-sm font-medium text-gray-700 mb-1">
                  Model
                </label>
                <select
                  id="model"
                  name="model"
                  value={formData.model}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="glm-4.6">GLM-4.6</option>
                  <option value="glm-4.5">GLM-4.5</option>
                  <option value="glm-4.5v">GLM-4.5V</option>
                  <option value="glm-4.5-air">GLM-4.5-Air</option>
                  <option value="glm-4.5-flash">GLM-4.5-Flash</option>
                </select>
              </div>

              <div>
                <label htmlFor="system_prompt" className="block text-sm font-medium text-gray-700 mb-1">
                  System Prompt
                </label>
                <textarea
                  id="system_prompt"
                  name="system_prompt"
                  value={formData.system_prompt}
                  onChange={handleInputChange}
                  required
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label htmlFor="temperature" className="block text-sm font-medium text-gray-700 mb-1">
                  Temperature: {formData.temperature}
                </label>
                <input
                  type="range"
                  id="temperature"
                  name="temperature"
                  value={formData.temperature}
                  onChange={handleInputChange}
                  min="0"
                  max="2"
                  step="0.1"
                  className="w-full"
                />
              </div>

              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={resetForm}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={createAgentMutation.isPending || updateAgentMutation.isPending}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                >
                  {createAgentMutation.isPending || updateAgentMutation.isPending 
                    ? 'Saving...' 
                    : (editingId ? 'Update Agent' : 'Create Agent')}
                </button>
              </div>
            </form>
          </div>
        )}

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {agents?.map((agent) => (
            <div
              key={agent.id}
              className="bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow flex flex-col h-full"
            >
              <div className="flex-grow">
                <h3 className="text-lg font-medium text-gray-900 mb-2">{agent.name}</h3>
                <p className="text-sm text-gray-600 mb-4 line-clamp-3">{agent.description}</p>
                <div className="flex items-center justify-between text-xs text-gray-500 mb-4">
                  <span className="bg-gray-100 px-2 py-1 rounded">{agent.model}</span>
                  <span className="bg-gray-100 px-2 py-1 rounded">Temp: {agent.temperature}</span>
                </div>
                
                {/* File Management Section */}
                <button
                  onClick={() => toggleFilesSection(agent.id)}
                  className="w-full text-left flex items-center justify-between bg-gray-50 hover:bg-gray-100 px-3 py-2 rounded text-sm transition-colors"
                >
                  <span className="flex items-center">
                    📁 Knowledge Files
                    <span className="ml-2 text-xs bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded">
                      View Files
                    </span>
                  </span>
                  <span className="text-gray-400">
                    {expandedAgentId === agent.id ? '▼' : '▶'}
                  </span>
                </button>
                
                {expandedAgentId === agent.id && (
                  <AgentFilesSection agentId={agent.id} />
                )}
              </div>
              
              <div className="border-t border-gray-100 pt-3 mt-auto flex justify-end space-x-2">
                <button
                  onClick={() => {
                     const url = `${window.location.origin}/tester/${agent.id}`;
                     navigator.clipboard.writeText(url);
                     alert('Tester link copied to clipboard!');
                  }}
                  className="text-sm text-purple-600 hover:text-purple-800 px-2 py-1 rounded hover:bg-purple-50 transition-colors flex items-center gap-1"
                >
                   Share
                </button>
                <button
                  onClick={() => handleEditClick(agent)}
                  className="text-sm text-blue-600 hover:text-blue-800 px-2 py-1 rounded hover:bg-blue-50 transition-colors"
                >
                  Edit
                </button>
                <button
                  onClick={() => handleDeleteClick(agent.id)}
                  className="text-sm text-red-600 hover:text-red-800 px-2 py-1 rounded hover:bg-red-50 transition-colors"
                  disabled={deleteAgentMutation.isPending}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}