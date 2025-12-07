/**
 * Team Analytics View
 * Compare team metrics and performance
 */
import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { teamsApi } from '../services/api';
import Breadcrumbs from '../components/layout/Breadcrumbs';
import { MetricsSkeleton } from '../components/common/LoadingSkeleton';
import { NoDataEmpty } from '../components/common/EmptyState';

export default function TeamAnalyticsView() {
  const { matchId } = useParams();
  const [selectedTeam, setSelectedTeam] = useState('home');
  const [loading, setLoading] = useState(false);
  const [metrics, setMetrics] = useState(null);

  React.useEffect(() => {
    if (matchId) {
      loadTeamMetrics();
    }
  }, [matchId, selectedTeam]);

  const loadTeamMetrics = async () => {
    setLoading(true);
    try {
      const response = await teamsApi.getTeamMetrics(matchId, selectedTeam);
      setMetrics(response.data);
    } catch (error) {
      console.error('Failed to load team metrics:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Breadcrumbs items={[
          { label: 'Dashboard', href: '/' },
          { label: 'Matches', href: '/matches' },
          { label: 'Team Analytics' }
        ]} />

        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900">Team Analytics</h1>
          <p className="text-slate-500 mt-1">
            Comprehensive team performance metrics and comparisons
          </p>
        </div>

        {/* Team Selector */}
        <div className="bg-white rounded-xl shadow-sm p-4 mb-6">
          <div className="flex space-x-2">
            <button
              onClick={() => setSelectedTeam('home')}
              className={`flex-1 px-6 py-3 rounded-lg font-medium transition-colors ${
                selectedTeam === 'home'
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              Home Team
            </button>
            <button
              onClick={() => setSelectedTeam('away')}
              className={`flex-1 px-6 py-3 rounded-lg font-medium transition-colors ${
                selectedTeam === 'away'
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              Away Team
            </button>
          </div>
        </div>

        {loading ? (
          <MetricsSkeleton />
        ) : !metrics ? (
          <NoDataEmpty />
        ) : (
          <div className="space-y-6">
            {/* Metrics Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <MetricCard
                title="Possession"
                value={`${metrics.possession_percentage || 0}%`}
                icon="⚽"
              />
              <MetricCard
                title="Total Distance"
                value={`${(metrics.total_distance / 1000).toFixed(1)} km`}
                icon="🏃"
              />
              <MetricCard
                title="Sprints"
                value={metrics.sprint_count || 0}
                icon="⚡"
              />
              <MetricCard
                title="Avg Speed"
                value={`${(metrics.avg_speed * 3.6).toFixed(1)} km/h`}
                icon="📊"
              />
            </div>

            {/* Team Heatmap Placeholder */}
            <div className="bg-white rounded-xl shadow-sm p-8">
              <h2 className="text-xl font-semibold text-slate-900 mb-4">Team Heatmap</h2>
              <div className="aspect-video bg-gradient-to-br from-green-600 to-green-800 rounded-lg flex items-center justify-center">
                <p className="text-white text-lg">Heatmap visualization coming soon</p>
              </div>
            </div>

            {/* Comparison Stats */}
            <div className="bg-white rounded-xl shadow-sm p-8">
              <h2 className="text-xl font-semibold text-slate-900 mb-6">Performance Metrics</h2>
              <div className="space-y-4">
                <StatBar label="High Intensity Runs" value={metrics.high_intensity_runs || 0} max={200} />
                <StatBar label="Passes Completed" value={metrics.passes_completed || 0} max={500} />
                <StatBar label="Defensive Actions" value={metrics.defensive_actions || 0} max={100} />
                <StatBar label="Attacking Third Entries" value={metrics.attacking_third_entries || 0} max={150} />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function MetricCard({ title, value, icon }) {
  return (
    <div className="bg-white rounded-xl shadow-sm p-6">
      <div className="flex items-center justify-between mb-2">
        <p className="text-sm text-slate-500">{title}</p>
        <span className="text-2xl">{icon}</span>
      </div>
      <p className="text-3xl font-bold text-slate-900">{value}</p>
    </div>
  );
}

function StatBar({ label, value, max }) {
  const percentage = (value / max) * 100;
  
  return (
    <div>
      <div className="flex justify-between items-center mb-2">
        <span className="text-sm font-medium text-slate-700">{label}</span>
        <span className="text-sm text-slate-900 font-semibold">{value}</span>
      </div>
      <div className="w-full bg-slate-100 rounded-full h-3">
        <div
          className="bg-blue-600 h-3 rounded-full transition-all duration-500"
          style={{ width: `${Math.min(percentage, 100)}%` }}
        />
      </div>
    </div>
  );
}
