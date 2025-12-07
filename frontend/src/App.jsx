/**
 * Main App Component with Routing
 */
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ToastProvider } from './components/common/Toast';
import TopNav from './components/layout/TopNav';

// Pages
import Dashboard from './pages/Dashboard';
import MatchesListView from './pages/MatchesListView';
import MatchDetailsView from './pages/MatchDetailsView';
import PlayerMetricsView from './pages/PlayerMetricsView';
import HeatmapView from './pages/HeatmapView';
import TacticalDashboard from './pages/TacticalDashboard';
import XTDashboard from './pages/XTDashboard';
import EventsTimeline from './pages/EventsTimeline';
import MatchReplayView from './pages/MatchReplayView';
import AssistantPage from './pages/AssistantPage';
import VideoUpload from './pages/VideoUpload';
import VideoProcessing from './pages/VideoProcessing';
import PitchView2D from './pages/PitchView2D';
import VideoOverlay from './pages/VideoOverlay';
import PlayerAnalytics from './pages/PlayerAnalytics';
import SinglePlayerAnalytics from './pages/SinglePlayerAnalytics';
import TeamAnalyticsView from './pages/TeamAnalyticsView';
import Settings from './pages/Settings';
import Reports from './pages/Reports';

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ToastProvider>
        <BrowserRouter>
          <div className="min-h-screen bg-slate-50">
            <TopNav />
            <Routes>
              {/* Home Dashboard */}
              <Route path="/" element={<Dashboard />} />
              
              {/* Matches List */}
              <Route path="/matches" element={<MatchesListView />} />
              
              {/* Match Details & Analytics */}
              <Route path="/matches/:matchId" element={<MatchDetailsView />} />
              <Route path="/matches/:matchId/players" element={<PlayerMetricsView />} />
              <Route path="/matches/:matchId/heatmap" element={<HeatmapView />} />
              
              {/* Phase 3: Tactical Analytics */}
              <Route path="/matches/:matchId/tactics" element={<TacticalDashboard />} />
              <Route path="/matches/:matchId/xt" element={<XTDashboard />} />
              <Route path="/matches/:matchId/events" element={<EventsTimeline />} />
              
              {/* Team Analytics */}
              <Route path="/matches/:matchId/teams" element={<TeamAnalyticsView />} />
              
              {/* Phase 4: Replay */}
              <Route path="/matches/:matchId/replay" element={<MatchReplayView />} />
              
              {/* Phase 5: AI Assistant */}
              <Route path="/assistant" element={<AssistantPage />} />
              
              {/* Upload */}
              <Route path="/upload" element={<VideoUpload />} />
              <Route path="/matches/:matchId/videos/:videoId/process" element={<VideoProcessing />} />
              <Route path="/videos/:videoId/pitch" element={<PitchView2D />} />
              <Route path="/videos/:videoId/overlay" element={<VideoOverlay />} />
              <Route path="/videos/:videoId/analytics" element={<PlayerAnalytics />} />
              <Route path="/videos/:videoId/player-analysis" element={<SinglePlayerAnalytics />} />
              
              {/* Settings & Reports */}
              <Route path="/settings" element={<Settings />} />
              <Route path="/reports" element={<Reports />} />
              
              {/* Default redirect */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </div>
        </BrowserRouter>
      </ToastProvider>
    </QueryClientProvider>
  );
}

export default App;
