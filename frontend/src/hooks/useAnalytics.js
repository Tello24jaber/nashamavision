/**
 * Custom React Hooks for Analytics
 */
import { useQuery } from '@tanstack/react-query';
import { analyticsApi, matchApi } from '../services/api';

// ============= Match Hooks =============

export const useMatches = () => {
  return useQuery({
    queryKey: ['matches'],
    queryFn: () => matchApi.getAll().then(res => res.data),
  });
};

export const useMatchAnalytics = (matchId) => {
  return useQuery({
    queryKey: ['matchAnalytics', matchId],
    queryFn: () => analyticsApi.getMatchAnalytics(matchId).then(res => res.data),
    enabled: !!matchId,
  });
};

export const useMatchPlayers = (matchId) => {
  return useQuery({
    queryKey: ['matchPlayers', matchId],
    queryFn: () => analyticsApi.getMatchPlayers(matchId).then(res => res.data),
    enabled: !!matchId,
  });
};

export const useMatch = (matchId) => {
  return useQuery({
    queryKey: ['match', matchId],
    queryFn: () => matchApi.getById(matchId).then(res => res.data),
    enabled: !!matchId,
  });
};

// ============= Player Metrics Hooks =============

export const usePlayerMetrics = (playerId, matchId) => {
  return useQuery({
    queryKey: ['playerMetrics', playerId, matchId],
    queryFn: () => analyticsApi.getPlayerMetrics(playerId, matchId).then(res => res.data),
    enabled: !!playerId,
  });
};

export const usePlayerTimeSeries = (playerId, metricType, matchId) => {
  return useQuery({
    queryKey: ['playerTimeSeries', playerId, metricType, matchId],
    queryFn: () =>
      analyticsApi.getPlayerTimeSeries(playerId, metricType, matchId).then(res => res.data),
    enabled: !!playerId && !!metricType,
  });
};

// ============= Heatmap Hooks =============

export const usePlayerHeatmap = (playerId, matchId) => {
  return useQuery({
    queryKey: ['playerHeatmap', playerId, matchId],
    queryFn: () => analyticsApi.getPlayerHeatmap(playerId, matchId).then(res => res.data),
    enabled: !!playerId,
  });
};

export const useTeamHeatmap = (matchId, teamSide) => {
  return useQuery({
    queryKey: ['teamHeatmap', matchId, teamSide],
    queryFn: () => analyticsApi.getTeamHeatmap(matchId, teamSide).then(res => res.data),
    enabled: !!matchId && !!teamSide,
  });
};
