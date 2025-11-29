import React from 'react';
import { Message } from '../types';

interface MessageManagementProps {
  message: Message;
  onEdit: (messageId: string, content: string) => void;
  onDelete: (messageId: string) => void;
  onCopy: (content: string) => void;
  isEditing: boolean;
  editingContent: string;
  onEditChange: (content: string) => void;
  onSaveEdit: () => void;
  onCancelEdit: () => void;
}

export default function MessageManagement({
  message,
  onEdit,
  onDelete,
  onCopy,
  isEditing,
  editingContent,
  onEditChange,
  onSaveEdit,
  onCancelEdit,
}: MessageManagementProps) {
  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: true 
    });
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getMessageStatus = () => {
    if (message.role === 'user') return 'sent';
    if (message.token_usage) return 'delivered';
    return 'processing';
  };

  const getStatusColor = () => {
    switch (getMessageStatus()) {
      case 'sent': return 'text-blue-500';
      case 'delivered': return 'text-green-500';
      case 'processing': return 'text-yellow-500';
      default: return 'text-gray-500';
    }
  };

  const getStatusIcon = () => {
    switch (getMessageStatus()) {
      case 'sent': return '✓';
      case 'delivered': return '✓✓';
      case 'processing': return '⏳';
      default: return '';
    }
  };

  return (
    <div className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} group`}>
      <div
        className={`max-w-2xl px-4 py-2 rounded-lg relative ${
          message.role === 'user'
            ? 'bg-blue-600 text-white'
            : 'bg-gray-100 text-gray-900'
        }`}
      >
        {isEditing ? (
          <div className="space-y-2">
            <textarea
              value={editingContent}
              onChange={(e) => onEditChange(e.target.value)}
              className="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={3}
            />
            <div className="flex space-x-2">
              <button
                onClick={onSaveEdit}
                className="px-2 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700"
              >
                Save
              </button>
              <button
                onClick={onCancelEdit}
                className="px-2 py-1 text-xs bg-gray-600 text-white rounded hover:bg-gray-700"
              >
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <>
            <div className="flex items-start justify-between">
              <div className="flex-1">
                {message.files && message.files.length > 0 && (
                  <div className="mb-2 space-y-1">
                    {message.files.map((file, index) => (
                      <div
                        key={index}
                        className={`flex items-center space-x-2 text-xs ${
                          message.role === 'user' ? 'text-blue-100' : 'text-gray-600'
                        }`}
                      >
                        <span>📎</span>
                        <span>{file.filename}</span>
                        <span>({formatFileSize(file.size)})</span>
                      </div>
                    ))}
                  </div>
                )}
                
                <p className="whitespace-pre-wrap break-words">{message.content}</p>
                
                {message.reasoning_content && (
                  <details className="mt-2">
                    <summary className={`text-xs cursor-pointer ${
                      message.role === 'user' ? 'text-blue-100' : 'text-gray-600'
                    }`}>
                      🧠 Show reasoning
                    </summary>
                    <div className={`mt-1 p-2 rounded text-xs ${
                      message.role === 'user' ? 'bg-blue-700 text-blue-100' : 'bg-gray-200 text-gray-700'
                    }`}>
                      <pre className="whitespace-pre-wrap">{message.reasoning_content}</pre>
                    </div>
                  </details>
                )}
              </div>
            </div>
            
            {/* Message metadata and actions */}
            <div className={`flex items-center justify-between mt-2 ${
              message.role === 'user' ? 'text-blue-100' : 'text-gray-500'
            }`}>
              <div className="flex items-center space-x-2">
                <span className="text-xs">
                  {formatTimestamp(message.timestamp)}
                </span>
                
                {/* Status indicator */}
                <span className={`text-xs ${getStatusColor()}`}>
                  {getStatusIcon()}
                </span>
                
                {message.token_usage && (
                  <span className="text-xs">
                    • {message.token_usage.total_tokens} tokens
                  </span>
                )}
                
                {message.model && (
                  <span className="text-xs">
                    • {message.model}
                  </span>
                )}
              </div>
              
              {/* Action buttons */}
              <div className="flex space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                  onClick={() => onCopy(message.content)}
                  className="p-1 hover:bg-gray-200 rounded text-xs"
                  title="Copy message"
                >
                  📋
                </button>
                
                {message.role === 'user' && (
                  <button
                    onClick={() => onEdit(message.id, message.content)}
                    className="p-1 hover:bg-gray-200 rounded text-xs"
                    title="Edit message"
                  >
                    ✏️
                  </button>
                )}
                
                <button
                  onClick={() => onDelete(message.id)}
                  className="p-1 hover:bg-red-200 rounded text-xs"
                  title="Delete message"
                >
                  🗑️
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}