/**
 * AssistantChat Component
 * 
 * Main chat interface for the AI Assistant
 */

import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import AssistantMessage from './AssistantMessage';
import useAssistant from '../../hooks/useAssistant';

const AssistantChat = ({ matchId, teamId, playerId, className = '' }) => {
  const navigate = useNavigate();
  const { messages, sendQuery, clearMessages, isLoading } = useAssistant();
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  
  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!inputValue.trim() || isLoading) return;
    
    const query = inputValue.trim();
    setInputValue('');
    
    try {
      await sendQuery(query, { matchId, teamId, playerId });
    } catch (error) {
      console.error('Failed to send query:', error);
    }
  };
  
  const handleActionClick = (action) => {
    // Handle different action types
    if (action.type === 'open_page') {
      const matchIdStr = action.match_id;
      const playerIdStr = action.player_id;
      
      // Route mapping
      const routes = {
        'match_details': `/matches/${matchIdStr}`,
        'player_metrics': `/matches/${matchIdStr}/players/${playerIdStr || ''}`,
        'heatmap': `/matches/${matchIdStr}/heatmap`,
        'tactical_dashboard': `/matches/${matchIdStr}/tactical`,
        'xt_dashboard': `/matches/${matchIdStr}/xt`,
        'events_timeline': `/matches/${matchIdStr}/events`,
        'replay': `/matches/${matchIdStr}/replay`,
      };
      
      const route = routes[action.page];
      if (route) {
        navigate(route);
      }
    } else if (action.type === 'open_replay') {
      const matchIdStr = action.match_id;
      const timestamp = action.timestamp;
      navigate(`/matches/${matchIdStr}/replay?t=${timestamp}`);
    }
  };
  
  const handleQuickQuestion = (question) => {
    setInputValue(question);
    inputRef.current?.focus();
  };
  
  // Quick question suggestions
  const quickQuestions = matchId
    ? [
        "Who covered the most distance?",
        "Which player had the highest xT?",
        "Compare stamina of both teams",
        "Show me the top 5 passes by xT",
        "What was the formation?",
      ]
    : [
        "What can you help me with?",
      ];
  
  return (
    <div className={`flex flex-col h-full bg-white rounded-lg shadow-lg ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-t-lg">
        <div className="flex items-center gap-3">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
          <div>
            <h3 className="font-bold">AI Assistant</h3>
            <p className="text-xs opacity-90">Ask me anything about the match</p>
          </div>
        </div>
        
        {messages.length > 0 && (
          <button
            onClick={clearMessages}
            className="px-3 py-1 text-xs bg-white bg-opacity-20 hover:bg-opacity-30 rounded transition-colors"
          >
            Clear
          </button>
        )}
      </div>
      
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {messages.length === 0 ? (
          <div className="text-center py-12">
            <div className="w-16 h-16 mx-auto mb-4 bg-blue-100 rounded-full flex items-center justify-center">
              <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h4 className="text-lg font-semibold text-gray-900 mb-2">
              Welcome to Nashama Vision Assistant
            </h4>
            <p className="text-sm text-gray-600 mb-6 max-w-md mx-auto">
              {matchId
                ? "I can answer questions about this match, players, tactics, and more. Try asking a question!"
                : "Select a match first to get started with detailed analytics."}
            </p>
            
            {/* Quick questions */}
            {matchId && (
              <div className="max-w-md mx-auto">
                <p className="text-xs font-semibold text-gray-700 mb-3">Try these questions:</p>
                <div className="space-y-2">
                  {quickQuestions.map((question, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleQuickQuestion(question)}
                      className="w-full px-4 py-2 text-sm text-left bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
                    >
                      {question}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <>
            {messages.map((message, idx) => (
              <AssistantMessage
                key={idx}
                message={message}
                onActionClick={handleActionClick}
              />
            ))}
            
            {isLoading && (
              <div className="flex justify-start mb-4">
                <div className="bg-gray-100 rounded-lg px-4 py-3">
                  <div className="flex items-center gap-2">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                    </div>
                    <span className="text-xs text-gray-600">Assistant is thinking...</span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </>
        )}
      </div>
      
      {/* Input area */}
      <div className="border-t p-4">
        {!matchId && (
          <div className="mb-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-sm text-yellow-800">
            ⚠️ Please select a match to enable detailed questions
          </div>
        )}
        
        <form onSubmit={handleSendMessage} className="flex gap-2">
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder={matchId ? "Ask a question..." : "Select a match first..."}
            disabled={isLoading}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
          />
          
          <button
            type="submit"
            disabled={!inputValue.trim() || isLoading}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
            Send
          </button>
        </form>
        
        <p className="text-xs text-gray-500 mt-2">
          Powered by AI • Answers based on match analytics data
        </p>
      </div>
    </div>
  );
};

export default AssistantChat;
