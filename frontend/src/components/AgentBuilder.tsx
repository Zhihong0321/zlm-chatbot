import React, { useState } from 'react';
import { useAgents, useCreateAgent, useUpdateAgent, useDeleteAgent } from '../hooks/useApi';

export default function AgentBuilder() {
  const { data: agents, isLoading, error } = useAgents();
  const createAgentMutation = useCreateAgent();
  const updateAgentMutation = useUpdateAgent();
  const deleteAgentMutation = useDeleteAgent();
  
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    model: 'glm-4.6',
    system_prompt: '',
    temperature: 0.7,
  });

  const [isFormVisible, setIsFormVisible] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);

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
              className="bg-white border border-gray-200 rounded-lg shadow-sm p-4 hover:shadow-md transition-shadow flex flex-col h-full"
            >
              <div className="flex-grow">
                <h3 className="text-lg font-medium text-gray-900 mb-2">{agent.name}</h3>
                <p className="text-sm text-gray-600 mb-4 line-clamp-3">{agent.description}</p>
                <div className="flex items-center justify-between text-xs text-gray-500 mb-4">
                  <span className="bg-gray-100 px-2 py-1 rounded">{agent.model}</span>
                  <span className="bg-gray-100 px-2 py-1 rounded">Temp: {agent.temperature}</span>
                </div>
              </div>
              
              <div className="border-t border-gray-100 pt-3 mt-auto flex justify-end space-x-2">
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