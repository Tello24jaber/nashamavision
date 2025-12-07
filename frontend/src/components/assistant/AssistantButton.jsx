/**
 * AssistantButton Component
 * 
 * Compact button to open assistant or navigate to assistant page
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';

const AssistantButton = ({ matchId, playerId, compact = false, className = '' }) => {
  const navigate = useNavigate();
  
  const handleClick = () => {
    const params = new URLSearchParams();
    if (matchId) params.append('match_id', matchId);
    if (playerId) params.append('player_id', playerId);
    
    navigate(`/assistant?${params.toString()}`);
  };
  
  if (compact) {
    return (
      <button
        onClick={handleClick}
        className={`p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors ${className}`}
        title="Ask AI Assistant"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
      </button>
    );
  }
  
  return (
    <button
      onClick={handleClick}
      className={`flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors ${className}`}
    >
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
      </svg>
      <span>Ask AI About This Match</span>
    </button>
  );
};

export default AssistantButton;
