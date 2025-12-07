// """
// API Service
// Centralized API client for backend communication
// """
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ============= Match API =============

export const matchApi = {
  getAll: () => apiClient.get('/api/v1/matches'),
  getById: (matchId) => apiClient.get(`/api/v1/matches/${matchId}`),
  create: (data) => apiClient.post('/api/v1/matches', data),
  update: (matchId, data) => apiClient.put(`/api/v1/matches/${matchId}`, data),
  delete: (matchId) => apiClient.delete(`/api/v1/matches/${matchId}`),
};

// ============= Video API =============

export const videoApi = {
  getByMatch: (matchId) => apiClient.get(`/api/v1/videos/match/${matchId}`),
  getById: (videoId) => apiClient.get(`/api/v1/videos/${videoId}`),
  upload: (matchId, file, onProgress) => {
    const formData = new FormData();
    formData.append('file', file);
    
    return apiClient.post(`/api/v1/videos/upload/${matchId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        const percentCompleted = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        if (onProgress) onProgress(percentCompleted);
      },
    });
  },
};

// ============= Analytics API =============

export const analyticsApi = {
  // Match analytics
  getMatchAnalytics: (matchId) =>
    apiClient.get(`/api/v1/analytics/matches/${matchId}`),
  
  getMatchPlayers: (matchId) =>
    apiClient.get(`/api/v1/analytics/matches/${matchId}/players`),
  
  // Player metrics
  getPlayerMetrics: (playerId, matchId) => {
    const params = matchId ? { match_id: matchId } : {};
    return apiClient.get(`/api/v1/analytics/players/${playerId}/metrics`, { params });
  },
  
  getPlayerMetricsDetailed: (playerId) =>
    apiClient.get(`/api/v1/analytics/players/${playerId}/metrics/all`),
  
  // Time series
  getPlayerTimeSeries: (playerId, metricType, matchId) => {
    const params = matchId ? { match_id: matchId } : {};
    return apiClient.get(
      `/api/v1/analytics/players/${playerId}/timeseries/${metricType}`,
      { params }
    );
  },
  
  // Heatmaps
  getPlayerHeatmap: (playerId, matchId) => {
    const params = matchId ? { match_id: matchId } : {};
    return apiClient.get(`/api/v1/analytics/players/${playerId}/heatmap`, { params });
  },
  
  getTeamHeatmap: (matchId, teamSide) =>
    apiClient.get(`/api/v1/analytics/matches/${matchId}/heatmap/team/${teamSide}`),
  
  // Team metrics
  getTeamMetrics: (teamSide, matchId) =>
    apiClient.get(`/api/v1/analytics/teams/${teamSide}/metrics`, {
      params: { match_id: matchId },
    }),
};

// ============= Tracks API =============

export const tracksApi = {
  getByVideo: (videoId) => apiClient.get(`/api/v1/tracks/video/${videoId}`),
  getById: (trackId) => apiClient.get(`/api/v1/tracks/${trackId}`),
  getTrackPoints: (trackId, limit) => {
    const params = limit ? { limit } : {};
    return apiClient.get(`/api/v1/tracks/${trackId}/points`, { params });
  },
};

// ============= Processing API =============

export const processingApi = {
  triggerProcessing: (videoId) =>
    apiClient.post(`/api/v1/processing/trigger/${videoId}`),

  getStatus: (videoId) =>
    apiClient.get(`/api/v1/processing/status/${videoId}`),
  
  // Simple processing (no Redis/Celery required)
  processSimple: (videoId) =>
    apiClient.post(`/api/v1/simple-processing/process/${videoId}`),
  
  getSimpleStatus: (videoId) =>
    apiClient.get(`/api/v1/simple-processing/status/${videoId}`),
  
  // Get tracking data for visualization
  getTracks: (videoId) =>
    apiClient.get(`/api/v1/simple-processing/tracks/${videoId}`),
};// ============= Replay API (Phase 4) =============

export const replayApi = {
  getSummary: (matchId) =>
    apiClient.get(`/api/v1/replay/match/${matchId}/summary`),
  
  getTimeline: (matchId, params = {}) => {
    const { startTime, endTime, fps = 10, includeBall = true, includeEvents = true } = params;
    return apiClient.get(`/api/v1/replay/match/${matchId}/timeline`, {
      params: {
        start_time: startTime,
        end_time: endTime,
        fps,
        include_ball: includeBall,
        include_events: includeEvents,
      },
    });
  },
  
  getPitchDimensions: () =>
    apiClient.get('/api/v1/replay/pitch/dimensions'),
};

// ============= Assistant API (Phase 5) =============

export const assistantApi = {
  query: (queryData) =>
    apiClient.post('/api/v1/assistant/query', queryData),
  
  testLLM: () =>
    apiClient.get('/api/v1/assistant/test'),
  
  health: () =>
    apiClient.get('/api/v1/assistant/health'),
};

// ============= Tactics API (Phase 3) =============

export const tacticsApi = {
  getMatchTactics: (matchId) =>
    apiClient.get(`/api/v1/tactics/match/${matchId}`),
  
  getTeamSnapshots: (matchId, teamSide) =>
    apiClient.get(`/api/v1/tactics/match/${matchId}/team/${teamSide}`),
  
  getFormationTimeline: (matchId) =>
    apiClient.get(`/api/v1/tactics/match/${matchId}/timeline`),
  
  getTransitions: (matchId) =>
    apiClient.get(`/api/v1/tactics/match/${matchId}/transitions`),
};

// ============= xT API (Phase 3) =============

export const xtApi = {
  getMatchXT: (matchId) =>
    apiClient.get(`/api/v1/xt/match/${matchId}`),
  
  getTeamXT: (matchId, teamSide) =>
    apiClient.get(`/api/v1/xt/match/${matchId}/team/${teamSide}`),
  
  getPlayerXT: (playerId) =>
    apiClient.get(`/api/v1/xt/player/${playerId}`),
  
  getXTEvents: (matchId) =>
    apiClient.get(`/api/v1/xt/events/${matchId}`),
  
  getXTGrid: () =>
    apiClient.get('/api/v1/xt/grid'),
};

// ============= Events API (Phase 3) =============

export const eventsApi = {
  getMatchEvents: (matchId, eventType = null) => {
    const params = eventType ? { event_type: eventType } : {};
    return apiClient.get(`/api/v1/events/match/${matchId}`, { params });
  },
  
  getPlayerEvents: (playerId) =>
    apiClient.get(`/api/v1/events/player/${playerId}`),
  
  getTeamEvents: (teamSide, matchId) =>
    apiClient.get(`/api/v1/events/team/${teamSide}/match/${matchId}`),
  
  getEventStats: (matchId) =>
    apiClient.get(`/api/v1/events/match/${matchId}/stats`),
};

// ============= Teams API =============

export const teamsApi = {
  getTeamMetrics: (matchId, teamSide) =>
    apiClient.get(`/api/v1/analytics/teams/${teamSide}/metrics`, {
      params: { match_id: matchId },
    }),
  
  getTeamHeatmap: (matchId, teamSide) =>
    apiClient.get(`/api/v1/analytics/matches/${matchId}/heatmap/team/${teamSide}`),
  
  compareTeams: (matchId) =>
    apiClient.get(`/api/v1/analytics/matches/${matchId}`),
};

// ============= Players API =============

export const playersApi = {
  getMatchPlayers: (matchId) =>
    apiClient.get(`/api/v1/analytics/matches/${matchId}/players`),
  
  getPlayerDetails: (playerId, matchId) =>
    apiClient.get(`/api/v1/analytics/players/${playerId}/metrics`, {
      params: { match_id: matchId },
    }),
  
  getPlayerHeatmap: (playerId, matchId) =>
    apiClient.get(`/api/v1/analytics/players/${playerId}/heatmap`, {
      params: { match_id: matchId },
    }),
  
  getPlayerTimeSeries: (playerId, metricType, matchId) =>
    apiClient.get(`/api/v1/analytics/players/${playerId}/timeseries/${metricType}`, {
      params: { match_id: matchId },
    }),
};

// ============= Upload API =============

export const uploadApi = {
  uploadVideo: (formData, config = {}) => {
    return apiClient.post('/api/v1/videos/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      ...config,
    });
  },
  
  getUploadStatus: (videoId) =>
    apiClient.get(`/api/v1/videos/${videoId}/status`),
  
  startProcessing: (videoId) =>
    apiClient.post(`/api/v1/processing/start/${videoId}`),
  
  getProcessingStatus: (jobId) =>
    apiClient.get(`/api/v1/processing/status/${jobId}`),
};

export default apiClient;
