/**
 * useAssistant Hook
 * 
 * Custom hook for interacting with the AI Assistant API
 */

import { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { assistantApi } from '../services/api';

/**
 * Hook for sending queries to the AI assistant
 */
export const useAssistant = () => {
  const [messages, setMessages] = useState([]);
  
  // Mutation for sending queries
  const queryMutation = useMutation({
    mutationFn: (queryData) => assistantApi.query(queryData),
    onSuccess: (response, variables) => {
      // Add user message
      setMessages(prev => [
        ...prev,
        {
          role: 'user',
          content: variables.query,
          timestamp: new Date().toISOString(),
        }
      ]);
      
      // Add assistant response
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: response.data.answer,
          data: response.data.data_used,
          actions: response.data.suggested_actions,
          followUps: response.data.follow_up_questions,
          timestamp: new Date().toISOString(),
        }
      ]);
    },
    onError: (error) => {
      // Add error message
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: `Sorry, I encountered an error: ${error.response?.data?.detail || error.message}`,
          error: true,
          timestamp: new Date().toISOString(),
        }
      ]);
    }
  });
  
  const sendQuery = async (query, context = {}) => {
    const queryData = {
      query,
      match_id: context.matchId || null,
      team_id: context.teamId || null,
      player_id: context.playerId || null,
    };
    
    return queryMutation.mutateAsync(queryData);
  };
  
  const clearMessages = () => {
    setMessages([]);
  };
  
  return {
    messages,
    sendQuery,
    clearMessages,
    isLoading: queryMutation.isPending,
    error: queryMutation.error,
  };
};

/**
 * Hook for testing LLM connection
 */
export const useLLMTest = () => {
  return useQuery({
    queryKey: ['assistant', 'llm-test'],
    queryFn: async () => {
      const response = await assistantApi.testLLM();
      return response.data;
    },
    retry: false,
    staleTime: Infinity, // Only test once per session
  });
};

/**
 * Hook for checking assistant health
 */
export const useAssistantHealth = () => {
  return useQuery({
    queryKey: ['assistant', 'health'],
    queryFn: async () => {
      const response = await assistantApi.health();
      return response.data;
    },
    refetchInterval: 30000, // Refetch every 30 seconds
  });
};

export default useAssistant;
