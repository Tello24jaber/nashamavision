/**
 * AssistantMessage Component
 * 
 * Displays a single message in the chat interface
 */

import React from 'react';

const AssistantMessage = ({ message, onActionClick }) => {
  const isUser = message.role === 'user';
  const isError = message.error;
  
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-[80%] ${isUser ? 'order-2' : 'order-1'}`}>
        {/* Message bubble */}
        <div
          className={`rounded-lg px-4 py-3 ${
            isUser
              ? 'bg-blue-600 text-white'
              : isError
              ? 'bg-red-50 text-red-900 border border-red-200'
              : 'bg-gray-100 text-gray-900'
          }`}
        >
          {/* Role label */}
          <div className="text-xs font-semibold mb-1 opacity-70">
            {isUser ? 'You' : 'AI Assistant'}
          </div>
          
          {/* Message content */}
          <div className="whitespace-pre-wrap text-sm leading-relaxed">
            {message.content}
          </div>
          
          {/* Structured data display */}
          {message.data && Object.keys(message.data).length > 0 && (
            <div className="mt-3 pt-3 border-t border-gray-200">
              <div className="text-xs font-semibold mb-2 opacity-70">Data Summary</div>
              <pre className="text-xs bg-white bg-opacity-50 p-2 rounded overflow-x-auto">
                {JSON.stringify(message.data, null, 2)}
              </pre>
            </div>
          )}
          
          {/* Suggested actions */}
          {message.actions && message.actions.length > 0 && (
            <div className="mt-3 pt-3 border-t border-gray-200">
              <div className="text-xs font-semibold mb-2 opacity-70">Suggested Actions</div>
              <div className="space-y-2">
                {message.actions.map((action, idx) => (
                  <button
                    key={idx}
                    onClick={() => onActionClick && onActionClick(action)}
                    className="w-full text-left px-3 py-2 bg-white bg-opacity-80 hover:bg-opacity-100 rounded text-xs font-medium transition-colors flex items-center gap-2"
                  >
                    {action.type === 'open_page' && (
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                      </svg>
                    )}
                    {action.type === 'open_replay' && (
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    )}
                    <span>{action.label}</span>
                  </button>
                ))}
              </div>
            </div>
          )}
          
          {/* Follow-up questions */}
          {message.followUps && message.followUps.length > 0 && (
            <div className="mt-3 pt-3 border-t border-gray-200">
              <div className="text-xs font-semibold mb-2 opacity-70">Follow-up Questions</div>
              <div className="space-y-1">
                {message.followUps.map((question, idx) => (
                  <div key={idx} className="text-xs opacity-80">
                    • {question}
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* Timestamp */}
          <div className="text-xs opacity-50 mt-2">
            {new Date(message.timestamp).toLocaleTimeString()}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AssistantMessage;
