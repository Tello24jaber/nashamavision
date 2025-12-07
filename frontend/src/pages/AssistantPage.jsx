/**
 * AssistantPage Component
 * 
 * Full-page AI Assistant interface
 */

import React, { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { matchApi } from '../services/api';
import AssistantChat from '../components/assistant/AssistantChat';
import { useLLMTest, useAssistantHealth } from '../hooks/useAssistant';

const AssistantPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [selectedMatchId, setSelectedMatchId] = useState(
    searchParams.get('match_id') || null
  );
  
  // Fetch matches for context selector
  const { data: matchesResponse, isLoading: loadingMatches } = useQuery({
    queryKey: ['matches'],
    queryFn: async () => {
      const response = await matchApi.getAll();
      return response.data;
    },
  });
  
  // Test LLM connection
  const { data: llmTest } = useLLMTest();
  const { data: health } = useAssistantHealth();
  
  const matches = matchesResponse?.matches || [];
  
  const handleMatchSelect = (matchId) => {
    setSelectedMatchId(matchId);
    if (matchId) {
      setSearchParams({ match_id: matchId });
    } else {
      setSearchParams({});
    }
  };
  
  const selectedMatch = matches.find(m => m.id === selectedMatchId);
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-blue-700 rounded-xl flex items-center justify-center">
                <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  Nashama Vision Assistant
                </h1>
                <p className="text-sm text-gray-600">
                  AI-powered football analytics assistant
                </p>
              </div>
            </div>
            
            {/* LLM Status */}
            {health && (
              <div className="flex items-center gap-2 px-3 py-2 bg-gray-50 rounded-lg">
                <div className={`w-2 h-2 rounded-full ${
                  health.llm_configured ? 'bg-green-500' : 'bg-yellow-500'
                }`}></div>
                <span className="text-xs font-medium text-gray-700">
                  {health.llm_provider === 'mock' ? 'Mock Mode' : `${health.llm_provider} Connected`}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>
      
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm p-4 mb-4">
              <h3 className="font-bold text-gray-900 mb-3 flex items-center gap-2">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
                Match Context
              </h3>
              
              {loadingMatches ? (
                <div className="text-sm text-gray-500">Loading matches...</div>
              ) : (
                <>
                  <select
                    value={selectedMatchId || ''}
                    onChange={(e) => handleMatchSelect(e.target.value || null)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                  >
                    <option value="">Select a match...</option>
                    {matches.map(match => (
                      <option key={match.id} value={match.id}>
                        {match.match_name || `Match ${match.id.slice(0, 8)}`}
                      </option>
                    ))}
                  </select>
                  
                  {selectedMatch && (
                    <div className="mt-3 p-3 bg-blue-50 rounded-lg">
                      <div className="text-xs font-semibold text-blue-900 mb-1">
                        Selected Match
                      </div>
                      <div className="text-sm text-blue-800">
                        {selectedMatch.match_name || 'Unnamed Match'}
                      </div>
                      {selectedMatch.match_date && (
                        <div className="text-xs text-blue-600 mt-1">
                          {new Date(selectedMatch.match_date).toLocaleDateString()}
                        </div>
                      )}
                    </div>
                  )}
                </>
              )}
            </div>
            
            {/* LLM Info */}
            {llmTest && (
              <div className="bg-white rounded-lg shadow-sm p-4 mb-4">
                <h3 className="font-bold text-gray-900 mb-3 flex items-center gap-2">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  AI Status
                </h3>
                
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Provider:</span>
                    <span className="font-medium text-gray-900">
                      {llmTest.provider}
                    </span>
                  </div>
                  
                  {llmTest.model && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Model:</span>
                      <span className="font-medium text-gray-900">
                        {llmTest.model}
                      </span>
                    </div>
                  )}
                  
                  <div className="flex justify-between">
                    <span className="text-gray-600">Status:</span>
                    <span className={`font-medium ${
                      llmTest.status === 'success' ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {llmTest.status === 'success' ? '✓ Connected' : '✗ Error'}
                    </span>
                  </div>
                  
                  {llmTest.error && (
                    <div className="mt-2 p-2 bg-red-50 rounded text-xs text-red-700">
                      {llmTest.error}
                    </div>
                  )}
                </div>
              </div>
            )}
            
            {/* Help section */}
            <div className="bg-white rounded-lg shadow-sm p-4">
              <h3 className="font-bold text-gray-900 mb-3 flex items-center gap-2">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                What Can I Ask?
              </h3>
              
              <div className="space-y-3 text-sm text-gray-700">
                <div>
                  <div className="font-medium text-gray-900 mb-1">Physical Metrics</div>
                  <ul className="space-y-1 text-xs">
                    <li>• Distance covered by players</li>
                    <li>• Speed and sprint analysis</li>
                    <li>• Stamina and workload</li>
                  </ul>
                </div>
                
                <div>
                  <div className="font-medium text-gray-900 mb-1">Tactical Analysis</div>
                  <ul className="space-y-1 text-xs">
                    <li>• Team formations</li>
                    <li>• Pressing intensity</li>
                    <li>• Defensive organization</li>
                  </ul>
                </div>
                
                <div>
                  <div className="font-medium text-gray-900 mb-1">Expected Threat (xT)</div>
                  <ul className="space-y-1 text-xs">
                    <li>• Dangerous players and zones</li>
                    <li>• xT gain per action</li>
                    <li>• Threat creation analysis</li>
                  </ul>
                </div>
                
                <div>
                  <div className="font-medium text-gray-900 mb-1">Events</div>
                  <ul className="space-y-1 text-xs">
                    <li>• Passes, carries, shots</li>
                    <li>• Key moments analysis</li>
                    <li>• Event-based statistics</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
          
          {/* Chat area */}
          <div className="lg:col-span-3">
            <AssistantChat
              matchId={selectedMatchId}
              className="h-[calc(100vh-12rem)]"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default AssistantPage;
