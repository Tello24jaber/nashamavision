/**
 * useReplayData Hook
 * Phase 4: Virtual Match Engine
 * 
 * Fetches and manages replay data from the API
 */
import { useQuery } from '@tanstack/react-query';
import { replayApi } from '../services/api';

export const useReplaySummary = (matchId) => {
  return useQuery({
    queryKey: ['replaySummary', matchId],
    queryFn: () => replayApi.getSummary(matchId).then((res) => res.data),
    enabled: !!matchId,
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 30 * 60 * 1000, // 30 minutes
  });
};

export const useReplayTimeline = (matchId, params = {}) => {
  const { startTime, endTime, fps = 10, includeBall = true, includeEvents = true } = params;
  
  return useQuery({
    queryKey: ['replayTimeline', matchId, startTime, endTime, fps, includeBall, includeEvents],
    queryFn: () => replayApi.getTimeline(matchId, params).then((res) => res.data),
    enabled: !!matchId,
    staleTime: 10 * 60 * 1000, // 10 minutes
    cacheTime: 30 * 60 * 1000, // 30 minutes
  });
};

export const usePitchDimensions = () => {
  return useQuery({
    queryKey: ['pitchDimensions'],
    queryFn: () => replayApi.getPitchDimensions().then((res) => res.data),
    staleTime: Infinity, // Never stale (static data)
    cacheTime: Infinity,
  });
};
