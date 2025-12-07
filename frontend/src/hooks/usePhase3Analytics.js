/**
 * Phase 3 Analytics Hooks
 * Custom hooks for tactical analysis, xT, and events
 */

import { useQuery } from '@tanstack/react-query';
import { tacticsApi, xtApi, eventsApi } from '../services/api';

// ============================================================================
// Tactical Analysis Hooks
// ============================================================================

export function useMatchTactics(matchId) {
  return useQuery({
    queryKey: ['tactics', 'match', matchId],
    queryFn: () => tacticsApi.getMatchTactics(matchId).then(res => res.data),
    enabled: !!matchId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useTacticalTimeline(matchId, teamSide) {
  return useQuery({
    queryKey: ['tactics', 'timeline', matchId, teamSide],
    queryFn: () => tacticsApi.getFormationTimeline(matchId, teamSide).then(res => res.data),
    enabled: !!matchId && !!teamSide,
    staleTime: 5 * 60 * 1000,
  });
}

export function useTeamTransitions(matchId, teamSide) {
  return useQuery({
    queryKey: ['tactics', 'transitions', matchId, teamSide],
    queryFn: () => tacticsApi.getTransitions(matchId, teamSide).then(res => res.data),
    enabled: !!matchId && !!teamSide,
    staleTime: 5 * 60 * 1000,
  });
}

// ============================================================================
// Expected Threat (xT) Hooks
// ============================================================================

export function useMatchXT(matchId) {
  return useQuery({
    queryKey: ['xt', 'match', matchId],
    queryFn: () => xtApi.getMatchXT(matchId).then(res => res.data),
    enabled: !!matchId,
    staleTime: 5 * 60 * 1000,
  });
}

export function usePlayerXT(playerId, matchId) {
  return useQuery({
    queryKey: ['xt', 'player', playerId, matchId],
    queryFn: () => xtApi.getPlayerXT(playerId, matchId).then(res => res.data),
    enabled: !!playerId && !!matchId,
    staleTime: 5 * 60 * 1000,
  });
}

export function useMatchXTEvents(matchId) {
  return useQuery({
    queryKey: ['xt', 'events', matchId],
    queryFn: () => xtApi.getXTEvents(matchId).then(res => res.data),
    enabled: !!matchId,
    staleTime: 5 * 60 * 1000,
  });
}

export function useXTGrid() {
  return useQuery({
    queryKey: ['xt', 'grid'],
    queryFn: () => xtApi.getXTGrid().then(res => res.data),
    staleTime: 60 * 60 * 1000, // 1 hour (static data)
  });
}

// ============================================================================
// Events Hooks
// ============================================================================

export function useMatchEvents(matchId, eventType = null) {
  return useQuery({
    queryKey: ['events', 'match', matchId, eventType],
    queryFn: () => eventsApi.getMatchEvents(matchId, eventType).then(res => res.data),
    enabled: !!matchId,
    staleTime: 5 * 60 * 1000,
  });
}

export function usePlayerEvents(playerId, matchId) {
  return useQuery({
    queryKey: ['events', 'player', playerId, matchId],
    queryFn: () => eventsApi.getPlayerEvents(playerId, matchId).then(res => res.data),
    enabled: !!playerId && !!matchId,
    staleTime: 5 * 60 * 1000,
  });
}

export function useTeamEventStats(matchId, teamSide) {
  return useQuery({
    queryKey: ['events', 'team', 'stats', matchId, teamSide],
    queryFn: () => eventsApi.getEventStats(matchId, teamSide).then(res => res.data),
    enabled: !!matchId && !!teamSide,
    staleTime: 5 * 60 * 1000,
  });
}
